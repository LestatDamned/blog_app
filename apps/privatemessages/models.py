from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse




class PrivateMessages(models.Model):
  sender = models.ForeignKey(to=User,verbose_name='Отправитель',on_delete=models.CASCADE,related_name='sender')
  receiver = models.ForeignKey(to=User,verbose_name='Получатель',on_delete=models.CASCADE,related_name='receiver')
  title = models.CharField(max_length=150,verbose_name='Тема сообщения')
  message = models.TextField(verbose_name='Текст сообщения')
  date_time = models.DateTimeField(auto_now_add=True,verbose_name='Время отправки')
  is_read = models.BooleanField(default=False)
  
  class Meta:
    verbose_name = 'Личное сообщение'
    verbose_name_plural = 'Личные сообщения'

  def __str__(self):
    return f'From {self.sender} to {self.receiver} {self.title}'
  
  def get_absolute_url(self):
      return reverse("messages_detail", kwargs={"pk": self.id})
