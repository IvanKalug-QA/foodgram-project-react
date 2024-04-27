import csv

from django.core.management.base import BaseCommand

from foods.models import Ingredients
from foodgram.settings import PARSE_CSV


class Command(BaseCommand):
    help = 'Импорт данных из csv файлов'

    def handle(self, *args, **options):
        ingredients_to_create = []
        with open(f'{PARSE_CSV}ingredients.csv',
                  'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                name, measurement_unit = row[0], row[1]
                ingredient = Ingredients(
                    name=name.strip(),
                    measurement_unit=measurement_unit.strip())
                ingredients_to_create.append(ingredient)
        Ingredients.objects.bulk_create(ingredients_to_create)
        self.stdout.write(self.style.SUCCESS('Данные успешно импортированы'))
