import csv
import json
import logging
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from ingredients.models import Ingredient

logger = logging.getLogger(__name__)


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

        file_path = data_dir / f'ingredients.{fmt}'
        if not file_path.exists():
            self.stderr.write(self.style.ERROR(f'Файл {file_path} не найден'))
            return

        try:
            with transaction.atomic():
                if fmt == 'csv':
                    with open(file_path, encoding='utf-8') as f:
                        reader = csv.reader(f)
                        for row in reader:
                            if len(row) < 2:
                                logger.warning(f'Пропущена строка: {row}')
                                continue
                            name, unit = row
                            Ingredient.objects.get_or_create(
                                name=name.strip(),
                                measurement_unit=unit.strip()
                            )
                else:  # json
                    with open(file_path, encoding='utf-8') as f:
                        data = json.load(f)
                        for item in data:
                            Ingredient.objects.get_or_create(
                                name=item['name'].strip(),
                                measurement_unit=item[
                                    'measurement_unit'
                                ].strip()
                            )
        except Exception as e:
            logger.exception("Ошибка при загрузке ингредиентов")
            self.stderr.write(self.style.ERROR(f'Ошибка: {e}'))
            return

        self.stdout.write(self.style.SUCCESS('Ингредиенты успешно загружены'))
