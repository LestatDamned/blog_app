from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django_recaptcha.fields import ReCaptchaField

from .models import Profile

UPDATE_FORM_WIDGET = forms.TextInput(attrs={'class':'form-control mb-1'})




class UserUpdateForm(forms.ModelForm):
  '''Форма обновления данных пользователя'''
  class Meta:
    model = User
    fields = ['username','email','first_name','last_name']
    widgets = {
      'username': UPDATE_FORM_WIDGET,
      'email': UPDATE_FORM_WIDGET,
      'first_name': UPDATE_FORM_WIDGET,
      'last_name': UPDATE_FORM_WIDGET,
    }

  def clean_email(self):
    '''Проверка эл почты на уникальность'''
    email = self.cleaned_data.get('email')
    username = self.cleaned_data.get('username')
    if email and User.objects.filter(email=email).exclude(username=username).exists():
      raise forms.ValidationError('Такой email адрес уже зарегестрирован')
    return email
  

class ProfileUpdateForm(forms.ModelForm):
  '''Форма обновления данных профиля пользователя'''
  class Meta:
    model = Profile
    fields = ['slug','birth_date','bio','avatar']
    widgets = {
      'slug': UPDATE_FORM_WIDGET,
      'birth_date': UPDATE_FORM_WIDGET,
      'bio': forms.Textarea(attrs={'rows':5,'class':'form-control mb-1'}),
      'avatar': forms.FileInput(attrs={'class':'form-control mb-1'})
    }

class UserRegisterForm(UserCreationForm):
  '''Переопределенная форма регистрации пользователей'''

  class Meta(UserCreationForm.Meta):
    fields = UserCreationForm.Meta.fields + ('email','first_name','last_name')

  def clean_email(self):
    '''Проверка email на уникальность'''
    email = self.cleaned_data.get('email')
    username = self.cleaned_data.get('username')
    if email and \
    User.objects.filter(email=email).exclude(username=username).exists():
      raise forms.ValidationError('Такой email уже существует')
    return email
  
  def __init__(self,*args, **kwargs):
    '''Обновление стилей формы регстрации'''
    super().__init__(*args, **kwargs)
    self.fields['username'].widget.attrs.update({"placeholder": "Придумайте свой логин"})
    self.fields['email'].widget.attrs.update({"placeholder": "Введите свой email"})
    self.fields['first_name'].widget.attrs.update({"placeholder": "Ваше имя"})
    self.fields['last_name'].widget.attrs.update({"placeholder": "Ваша фамилия"})
    self.fields['password1'].widget.attrs.update({"placeholder": "Придумайте свой пароль"})
    self.fields['password2'].widget.attrs.update({"placeholder": "Повторите придуманный пароль"})
    for field in self.fields:
      self.fields[field].widget.attrs.update({'class':'form-control','autocomplete':'off'})


class UserLoginForm(AuthenticationForm):
  '''Форма авторизации на сайте'''

  recaptcha = ReCaptchaField()

  class Meta:
    model = User
    fields = ['username','password','recaptcha']

  def __init__(self,*args, **kwargs):
    '''Обновление стилей формы авторизации'''
    super().__init__(*args, **kwargs)
    self.fields['username'].widget.attrs['placeholder'] = 'Логин пользователя'
    self.fields['username'].widget.attrs['class'] = 'form-control'
    self.fields['password'].widget.attrs['placeholder'] = 'Пароль пользователя'
    self.fields['password'].widget.attrs['class'] = 'form-control'
    self.fields['username'].label = 'Логин'
