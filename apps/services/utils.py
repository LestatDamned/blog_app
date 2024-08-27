from uuid import uuid4
from pytils.translit import slugify


def unique_slugify(instance, base_slug):
  """Генератор уникальных СЛАГ для модели, чтобы избежать дублирования."""
  slug = slugify(base_slug)
  model = instance.__class__
  unique_slug = slug
  num = 1
  
  while model.objects.filter(slug=unique_slug).exclude(id=instance.id).exists():
      unique_slug = f"{slug}-{num}"
      num += 1
  return unique_slug