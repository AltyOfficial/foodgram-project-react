# Generated by Django 3.2.16 on 2022-11-25 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20221125_2251'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='recipe',
            index=models.Index(fields=['pub_date'], name='pub_date_idx'),
        ),
    ]
