import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Import tags from CSV'

    def handle(self, *args, **options):
        base_dir = os.path.dirname(settings.BASE_DIR)
        file_path = os.path.join(base_dir, 'data', 'tags.csv')
        with open(file_path, mode='r', encoding='utf-8') as file:
            for row in csv.reader(file):
                try:
                    tag = Tag.objects.get(name=row[0])
                    self.stdout.write(
                        self.style.WARNING(
                            f"Tag with name {row[0]} already "
                            f"exists.Skipping..."
                        )
                    )

                except Tag.DoesNotExist:
                    tag = Tag.objects.create(
                        name=row[0],
                        slug=row[1],
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully imported tag: {tag.name}"
                        )
                    )
