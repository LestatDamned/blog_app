from django.urls import reverse
from django.shortcuts import get_object_or_404,redirect
from django.views.generic import ListView, CreateView, FormView
from django.contrib.auth.models import User
from django.db.models import Q, Max
from django.http import HttpResponseRedirect

from .models import PrivateMessages
from .forms import MessagesForm,ChatForm


class MessagesViewInbox(ListView):
  model = PrivateMessages
  template_name = 'messages/messages_inbox.html'
  context_object_name = 'privatemessages'
  paginate_by = 5
  tag = None

  def get_queryset(self):
    queryset = PrivateMessages.objects.filter(receiver=self.request.user).order_by('-date_time')
    return queryset
  
  def get_context_data(self,**kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = f'Сообщения для: {self.request.user}'
    return context


class DialogsListView(ListView):
  model = User
  template_name = 'messages/dialogs_list.html'
  context_object_name = 'dialogs'
  paginate_by = 5

  def get_queryset(self):
    user = self.request.user
    dialogs = PrivateMessages.objects.filter(
        Q(sender=user) | Q(receiver=user)
    ).values(
        'receiver_id', 
        'receiver__username'
    ).annotate(
        last_message_date=Max('date_time')
    ).order_by('receiver_id')
    return dialogs


class SendMessagesView(CreateView):
  model = PrivateMessages
  form_class = MessagesForm
  template_name = 'messages/send_messages.html'
  extra_context = {'title':'Отправка сообщений'}

  def form_valid(self, form):
      form.instance.sender = self.request.user
      self.object = form.save()
      return super().form_valid(form)
  



# class MessagesListView(ListView,FormView):
#   model = PrivateMessages
#   form_class = ChatForm
#   template_name = 'messages/message_detail.html'
#   context_object_name = 'privatemessages'
#   paginate_by = 5

#   def get_context_data(self, **kwargs):
#     context = super().get_context_data(**kwargs)
#     receiver_id = self.kwargs['receiver_id']
#     receiver_user = get_object_or_404(User, id=receiver_id)
#     context['title'] = f'Диалог с {receiver_user.username}'
#     context['receiver'] = receiver_user 
#     context['form'] = self.form_class
#     return context
  
#   def form_valid(self,form):
#     form.instance.receiver  = get_object_or_404(User, id=form.cleaned_data['receiver'])
#     form.instance.sender = self.request.user
#     return super().form_valid(form)

#   def get_form(self,form_class=None):
#     form = super().get_form(form_class)
#     receiver_id = self.kwargs['receiver_id']
#     form.fields['receiver'].initial = receiver_id
#     return form
  
#   def get_queryset(self):
#     user = self.request.user
#     receiver_id = self.kwargs['receiver_id']
#     return PrivateMessages.objects.filter(
#         Q(sender=user, receiver_id=receiver_id) |
#         Q(sender_id=receiver_id, receiver_id=user.id)
#     ).order_by('-date_time')

#   def get_success_url(self):
#     # return reverse('messages_detail', kwargs={'receiver_id': self.kwargs['receiver_id']})
#     return self.request.path
class MessagesListView(ListView, FormView):
    model = PrivateMessages
    template_name = 'messages/message_detail.html'
    context_object_name = 'privatemessages'
    paginate_by = 5  # Количество сообщений на странице
    form_class = ChatForm  # Форма для отправки сообщений

    def get_queryset(self):
        user = self.request.user
        receiver_id = self.kwargs['receiver_id']

        return PrivateMessages.objects.filter(
            Q(sender=user, receiver_id=receiver_id) |
            Q(sender_id=receiver_id, receiver=user)
        ).exclude(sender=user,receiver=user).order_by('-date_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        receiver_id = self.kwargs['receiver_id']
        receiver_user = get_object_or_404(User, id=receiver_id)
        context['title'] = f'Диалог с {receiver_user.username}'
        context['receiver'] = receiver_user
        context['form'] = self.get_form()  # Передача формы в контекст
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.sender = self.request.user
        form.instance.receiver = get_object_or_404(User, id=self.kwargs['receiver_id'])
        form.save()
        # Перенаправление на ту же страницу с сохранением пагинации
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        # Обеспечиваем наличие object_list при обработке неверной формы
        self.object_list = self.get_queryset()  # Загрузка списка сообщений
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_success_url(self):
        page = self.request.GET.get('page', 1)
        return f"{self.request.path}?page={page}"