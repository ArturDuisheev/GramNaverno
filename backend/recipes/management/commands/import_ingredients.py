import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from recipes.models import Ingredient, MeasurementUnit


class Command(BaseCommand):
    help = 'Import ingredients from CSV'

    def handle(self, *args, **options):
        base_dir = os.path.dirname(settings.BASE_DIR)
        file_path = os.path.join(base_dir, 'data', 'ingredients.csv')
        file_path = os.path.join(base_dir, 'data', 'ingredients.csv')
        with open(file_path, mode='r', encoding='utf-8') as file:
            for row in csv.reader(file):
                try:
                    ingredient = Ingredient.objects.get(name=row[0])
                    self.stdout.write(
                        self.style.WARNING(
                            f"Ingredient with name {row[0]} already "
                            f"exists.Skipping..."
                        )
                    )
                    measurement_unit = MeasurementUnit.objects.get(name=row[1])
                    self.stdout.write(
                        self.style.WARNING(
                            f"MeasurementUnit with name {row[1]} already "
                            f"exists.Skipping..."
                        )
                    )

                except Ingredient.DoesNotExist:
                    measurement_unit = MeasurementUnit.objects.create(
                        short_name=row[1]
                    )
                    ingredient = Ingredient.objects.create(
                        name=row[0],
                        measurement_unit=measurement_unit,
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully imported ingredient: "
                            f"{ingredient.name}"
                        )
                    )
