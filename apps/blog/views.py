from typing import Any
from django.shortcuts import render,redirect
from django.views.generic import ListView, DetailView, CreateView,UpdateView,View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse, JsonResponse
from taggit.models import Tag
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.forms import formset_factory

from .forms import PostCreateForm,PostUpdateForm,CommentCreateForm, CategoryCreateForm
from .models import Post, Category,Comment,Rating,RatingComment
from ..services.mixins import AuthorRequiredMixin



class PostListView(ListView):
  '''Представление: список постов'''

  model = Post
  template_name = 'blog/post_list.html'
  context_object_name = 'posts'
  paginate_by = 5
  queryset = Post.custom.all()
  extra_context = {'title':'Главная страница'}


  
class PostDetailView(DetailView):
  '''Представление: поста'''

  model = Post
  template_name = 'blog/post_detail.html'
  context_object_name = 'post'
  extra_context = {'form': CommentCreateForm}

  def get_context_data(self, **kwargs) -> dict[str, Any]:
      context = super().get_context_data(**kwargs)
      context["title"] = self.object.title
      return context
  

class PostFromCategory(ListView):
  '''Представление: постов по категории'''

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
  


CategoryFormSet = formset_factory(CategoryCreateForm, extra=1, can_delete=False)


class PostCreateView(FormView):
  '''Представление: поста на сайте'''

  template_name = 'blog/post_create.html'
  form_class = PostCreateForm
  extra_context = {'title':'Создание поста'}

  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context['post_form'] = self.get_form()
      context['category_formset'] = CategoryFormSet()
      return context

  def post(self, request, *args, **kwargs):
      post_form = self.form_class(request.POST, request.FILES)
      category_formset = CategoryFormSet(request.POST)
      print("POST Data:", request.POST)
      print("POST Files:", request.FILES)
      print("Post Form Errors:", post_form.errors)
      print("Category Form Errors:", category_formset.errors)

      if post_form.is_valid():
          post_cleaned_data = post_form.cleaned_data
          print("Post Form Cleaned Data:", post_form.cleaned_data)
          selected_category = post_cleaned_data['category']

          if not selected_category:
              if category_formset.is_valid():
                category_form = category_formset.forms[0]
                new_category = category_form.save()
                post_form.instance.category = new_category
              else:
                return self.render_to_response(self.get_context_data(
                    post_form=post_form,
                    category_formset=category_formset,
                    error='Вы должны выбрать категорию или создать новую'
                ))

          post_form.save()
          return redirect(reverse_lazy('home'))

      return self.render_to_response(self.get_context_data(
          post_form=post_form,
          category_formset=category_formset
      ))

class PostUpdateView(AuthorRequiredMixin,SuccessMessageMixin,UpdateView):
  '''Представление: обновление постов на сайте'''

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
  '''Представление: для создания деревотивных комментариев'''

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


class RatingCommentCreateView(View):
  '''Представление для обработки рейтинга комментария'''

  model = RatingComment

  def post(self, request, *args, **kwargs):
    comment_id = int(request.POST.get('comment_id'))
    value = int(request.POST.get('value'))
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
    
    user = request.user if request.user.is_authenticated else None
    
    rating, created = self.model.objects.get_or_create(
        comment_id=comment_id,
        ip_address=ip,
        defaults={'value': value, 'user': user},
    )
    
    if not created:  
        if rating.value == value:  
            rating.delete()
        else:  
            rating.value = value
            rating.user = user
            rating.save()
    
    comment = Comment.objects.get(pk=comment_id)
    return JsonResponse({'rating_sum': comment.get_sum_rating()})