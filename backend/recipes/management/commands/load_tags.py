import csv

from django.core.management.base import BaseCommand
from recipes.models import Tag

from backend.settings import BASE_DIR


class Command(BaseCommand):
    help = 'Загрузка ингредиентов в БД из .csv'

    def handle(self, **kwargs):
        data_path = BASE_DIR / 'data'
        with open(
            f'{data_path}/tags.csv', 'r', encoding='UTF-8'
        ) as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                name = row[0]
                color = row[1]
                slug = row[2]
                Tag.objects.get_or_create(
                    name=name,
                    color=color,
                    slug=slug
                )
        self.stdout.write(self.style.SUCCESS('SUCCESS'))
