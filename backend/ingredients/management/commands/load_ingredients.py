import csv
import json
from django.core.management.base import BaseCommand
from ingredients.models import Ingredient
from django.conf import settings
from pathlib import Path


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из data/ingredients.csv или ingredients.json'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            choices=['csv', 'json'],
            default='csv',
            help='Формат файла: csv или json (по умолчанию csv)'
        )

    def handle(self, *args, **options):
        data_dir = Path(settings.BASE_DIR) / 'data'
        fmt = options['format']

        if fmt == 'csv':
            file_path = data_dir / 'ingredients.csv'
            with open(file_path, encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    name, unit = row
                    Ingredient.objects.get_or_create(
                        name=name.strip(),
                        measurement_unit=unit.strip()
                    )
        else:
            file_path = data_dir / 'ingredients.json'
            with open(file_path, encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    Ingredient.objects.get_or_create(
                        name=item['name'].strip(),
                        measurement_unit=item['measurement_unit'].strip()
                    )

        self.stdout.write(self.style.SUCCESS('Ингредиенты успешно загружены'))
