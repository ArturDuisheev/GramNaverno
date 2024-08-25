from pathlib import Path
from core.config.helpers.env_reader import env

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = '123'
DEBUG = True
ALLOWED_HOSTS = ['*']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
