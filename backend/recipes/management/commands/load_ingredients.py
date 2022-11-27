import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient

from backend.settings import BASE_DIR


class Command(BaseCommand):
    help = 'Загрузка ингредиентов в БД из .csv'

    def handle(self, **kwargs):
        data_path = BASE_DIR / 'data'
        with open(
            f'{data_path}/ingredients.csv', 'r', encoding='UTF-8'
        ) as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                name, measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit
                )
        self.stdout.write(self.style.SUCCESS('SUCCESS'))
