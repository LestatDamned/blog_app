from typing import Any
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http.response import HttpResponseRedirect
from django.shortcuts import render,redirect
from .models import Post, Category,Comment,Rating
from django.views.generic import ListView, DetailView, CreateView,UpdateView,View
from .forms import PostCreateForm,PostUpdateForm,CommentCreateForm, CategoryCreateForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from ..services.mixins import AuthorRequiredMixin
from django.http import HttpResponse, JsonResponse
from taggit.models import Tag
from django.urls import reverse_lazy


class PostListView(ListView):
  model = Post
  template_name = 'blog/post_list.html'
  context_object_name = 'posts'
  paginate_by = 5
  queryset = Post.custom.all()
  extra_context = {'title':'Главная страница'}


  
class PostDetailView(DetailView):
  model = Post
  template_name = 'blog/post_detail.html'
  context_object_name = 'post'
  extra_context = {'form': CommentCreateForm}

  def get_context_data(self, **kwargs) -> dict[str, Any]:
      context = super().get_context_data(**kwargs)
      context["title"] = self.object.title
      return context
  

class PostFromCategory(ListView):
  template_name = 'blog/post_list.html'
  context_object_name = 'posts'
  category = None
  paginate_by = 5

  def get_queryset(self):
    self.category = Category.objects.get(slug=self.kwargs['slug'])
    queryset = Post.custom.filter(category__slug=self.category.slug)
    if not queryset:
      sub_cat = Category.objects.filter(parent=self.category)
      queryset = Post.custom.filter(category__in=sub_cat)
    return queryset
  
  def get_context_data(self,**kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = f'Записи из категории:{self.category.title}'
    return context
  

class PostCreateView(LoginRequiredMixin,CreateView):
  '''Представление: создание материалов на сайте'''

  model = Post
  template_name = 'blog/post_create.html'
  form_class = PostCreateForm
  second_form_class = CategoryCreateForm
  login_url = 'home'
  extra_context = {'title':'Добавление статьи на сайт'}

  def get_context_data(self,**kwargs):
    context = super().get_context_data(**kwargs)
    if 'category_form' not in context:
      context['category_form'] = self.second_form_class()
    return context
  
  def post(self,request,*args, **kwargs):
    self.object = None
    post_form = self.get_form(self.get_form_class())
    category_form = self.second_form_class(request.POST)
    if post_form.is_valid() and category_form.is_valid():
      return self.form_valid(post_form,category_form)
    else:
      return self.form_invalid(post_form,category_form)

  def form_valid(self,post_form,category_form):
    category = category_form.save()
    post_form.instance.author = self.request.user
    post = post_form.save(commit=False)
    post.category = category
    post.save()
    return super().form_valid(post_form)
  
  def get_success_url(self) -> str:
    return reverse_lazy('post_detail',kwargs={'slug':self.object.slug})
  

class PostUpdateView(AuthorRequiredMixin,SuccessMessageMixin,UpdateView):
  '''Представление: обновления материала на сайте'''

  model = Post
  template_name = 'blog/post_update.html'
  context_object_name = 'post'
  form_class = PostUpdateForm
  login_url = 'home'
  success_message = 'Запись была успешно обновлена!'

  def get_context_data(self, **kwargs) -> dict[str, Any]:
    context = super().get_context_data(**kwargs)
    context["title"] = f'Обновление статьи:{self.object.title}'
    return context

  def form_valid(self, form):
      form.save()
      return super().form_valid(form)
  

class CommentCreateView(LoginRequiredMixin,CreateView):
  '''Представление: для создания деревотивных комментарий'''

  form_class = CommentCreateForm

  def is_ajax(self):
    return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'
  
  def form_invalid(self, form):
    if self.is_ajax():
      return JsonResponse({'error': form.errors},status=400)
    return super().form_invalid(form)
  
  def form_valid(self, form):
    comment = form.save(commit=False)
    comment.post_id = self.kwargs.get('pk')
    comment.author = self.request.user
    comment.parent_id = form.cleaned_data.get('parent')
    comment.save()

    if self.is_ajax():
      return JsonResponse({
        'is_child': comment.is_child_node(),
        'id': comment.id,
        'author': comment.author.username,
        'parent_id': comment.parent_id,
        'time_create': comment.time_create.strftime('%Y-%b-%d %H:%M:%S'),
        'avatar': comment.author.profile.avatar.url,
        'content': comment.content,
        'get_absolute_url': comment.author.profile.get_absolute_url()
      },status=200)
    
    return redirect(comment.post.get_absolute_url())
  
  def handle_no_permission(self):
    return JsonResponse({'error':'Необходимо авторизоваться для добавления комментариев'},status=400)
  


class PostByTagListView(ListView):
  '''Представление: отображение постов по тегам'''

  model = Post
  template_name = 'blog/post_list.html'
  context_object_name = 'posts'
  paginate_by = 10
  tag = None

  def get_queryset(self):
    self.tag = Tag.objects.get(slug=self.kwargs['tag'])
    queryset = Post.objects.filter(tags__slug=self.tag.slug)
    return queryset
  
  def get_context_data(self,**kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = f'Статьи по тегу:{self.tag.name}'
    return context
  

class RatingCreateView(View):
    '''Представление: рейтинг поста'''
    model = Rating

    def post(self,request,*args, **kwargs):
      post_id = request.POST.get('post_id')
      value = int(request.POST.get('value'))
      x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
      ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
      user = request.user if request.user.is_authenticated else None
      rating,created = self.model.objects.get_or_create(
        post_id = post_id,
        ip_address = ip,
        defaults = {'value':value,'user':user},
      )
      if not created:
        if rating.value == value:
          rating.delete()
          return JsonResponse({'status':'deleted','rating_sum': rating.post.get_sum_rating()})
        else:
          rating.value = value
          rating.user = user
          rating.save()
          return JsonResponse({'status':'updated','rating_sum':rating.post.get_sum_rating()})
      return JsonResponse({'status':'created','rating_sum':rating.post.get_sum_rating()})
    

def tr_handler404(request,exception):
  '''Представление: обработка ошибки 404'''
  return render(request=request,
    template_name='errors/error_page.html', status=404,context={
      'title': 'Страница не найдена: 404',
      'error_message': 'К сожалению такая страница была не найдена',
    })


def tr_hadler500(request):
  '''Представление: обработка ошибки 500'''
  return render(request=request,
    template_name='errors/error_page.html', status=500,context={
      'title': 'Ошибка сервера: 500',
      'error_message': 'Внутренняя ошибка сайта, вернитесь на главную страницу, отчёт об ошибке мы направим администрации сайта',
    })


def tr_handler403(request, exception):
    '''Представление: обработка ошибки 403'''
    return render(request=request, template_name='errors/error_page.html', status=403, context={
        'title': 'Ошибка доступа: 403',
        'error_message': 'Доступ к этой странице ограничен',
    })