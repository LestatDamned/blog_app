from django.contrib import admin

from .models import PrivateMessages

@admin.register(PrivateMessages)
class PrivateMessagesAdmin(admin.ModelAdmin):
  pass

