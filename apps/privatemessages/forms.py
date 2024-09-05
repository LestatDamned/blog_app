from django import forms

from .models import PrivateMessages
class MessagesForm(forms.ModelForm):

  class Meta:
    model = PrivateMessages
    fields = ['message','receiver']

  def __init__(self,*args, **kwargs):
    '''Обновление стилей формы под Bootstrap'''
    super().__init__(*args, **kwargs)
    for field in self.fields:
      self.fields[field].widget.attrs.update({
        'class':'form-control',
        'autocomplete':'off'
      })


class ChatForm(forms.ModelForm):

  class Meta:
    model = PrivateMessages
    fields = ['message']

  def __init__(self,*args, **kwargs):
    '''Обновление стилей формы под Bootstrap'''
    super().__init__(*args, **kwargs)
    for field in self.fields:
      self.fields[field].widget.attrs.update({
        'class':'form-control',
        'autocomplete':'off'
      })