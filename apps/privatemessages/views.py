from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView,UpdateView,View

from .models import PrivateMessages
from .forms import MessagesForm


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


class MessagesViewSent(ListView):
  model = PrivateMessages
  template_name = 'messages/sent_messages.html'
  context_object_name = 'privatemessages'
  paginate_by = 5
  tag = None

  def get_queryset(self):
    queryset = PrivateMessages.objects.filter(sender=self.request.user).order_by('-date_time')
    return queryset
  
  def get_context_data(self,**kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = f'Сообщения от: {self.request.user}'
    return context


class SendMessagesView(CreateView):
  model = PrivateMessages
  form_class = MessagesForm
  template_name = 'messages/send_messages.html'
  extra_context = {'title':'Отправка сообщений'}

  def form_valid(self, form):
      form.instance.sender = self.request.user
      self.object = form.save()
      return super().form_valid(form)
  


class MessagesDetailView(DetailView):
  model = PrivateMessages
  template_name = 'messages/message_detail.html'
  context_object_name = 'privatemessages'
  
  def get_context_data(self, **kwargs):
    context =  super().get_context_data(**kwargs)
    context['title'] = self.object.title
    return context
  