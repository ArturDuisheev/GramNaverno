import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from users.models import User


class Command(BaseCommand):
    help = 'Import users from CSV'

    def handle(self, *args, **options):
        base_dir = os.path.dirname(settings.BASE_DIR)
        file_path = os.path.join(base_dir, 'data', 'users.csv')
        file_path = os.path.join(base_dir, 'data', 'users.csv')
        with open(file_path, mode='r', encoding='utf-8') as file:
            for row in csv.reader(file):
                try:
                    user = User.objects.get(username=row[3])
                    self.stdout.write(
                        self.style.WARNING(
                            f"User with username {row[2]} already "
                            f"exists.Skipping..."
                        )
                    )
                except User.DoesNotExist:

                    user = User.objects.create(
                        first_name=row[0],
                        last_name=row[1],
                        username=row[2],
                        email=row[3],
                        password=row[4]
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully imported users: {user.username}"
                        )
                    )
