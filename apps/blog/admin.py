from django.contrib import admin
from .models import Post, Category,Comment,Rating,RatingComment
from django_mptt_admin.admin import DjangoMpttAdmin

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
  '''Админ-панель модели записей'''
  prepopulated_fields = {'slug':['title']}

@admin.register(Category)
class CategoryAdmin(DjangoMpttAdmin):
  '''Админ панель модели категорий'''
  prepopulated_fields = {'slug':['title']}

@admin.register(Comment)
class CommentAdminPage(DjangoMpttAdmin):
  '''Админ-панель модели комментариев'''
  pass


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
  '''Админ-панель модели рейтинга'''
  pass

@admin.register(RatingComment)
class RatingAdmin(admin.ModelAdmin):
  '''Админ-панель модели рейтинга'''
  pass
