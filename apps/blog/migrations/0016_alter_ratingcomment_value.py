# Generated by Django 5.0.6 on 2024-09-05 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0015_delete_privatemessages'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ratingcomment',
            name='value',
            field=models.IntegerField(choices=[(1, 'Нравится'), (-1, 'Не нравится')], verbose_name='Значение'),
        ),
    ]
