from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse




class PrivateMessages(models.Model):
  sender = models.ForeignKey(to=User,verbose_name='Отправитель',on_delete=models.CASCADE,related_name='sender')
  receiver = models.ForeignKey(to=User,verbose_name='Получатель',on_delete=models.CASCADE,related_name='receiver')
  message = models.TextField(verbose_name='Текст сообщения')
  date_time = models.DateTimeField(auto_now_add=True,verbose_name='Время отправки')
  is_read = models.BooleanField(default=False)
  
  class Meta:
    verbose_name = 'Личное сообщение'
    verbose_name_plural = 'Личные сообщения'
    ordering = ['date_time']

  def __str__(self):
    return f'От {self.sender} для {self.receiver} {self.message[:50]}'
  
  def get_absolute_url(self):
    return reverse("messages_detail", kwargs={"receiver_id": self.receiver_id})
