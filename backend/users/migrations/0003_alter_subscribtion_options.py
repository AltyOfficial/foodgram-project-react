# Generated by Django 3.2.16 on 2022-11-12 17:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20221112_2011'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscribtion',
            options={'ordering': ['-user'], 'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
    ]