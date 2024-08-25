import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent





#DATABASES = {
    #'default': {
        #"ENGINE": "django.db.backends.postgresql",
        #"NAME": os.getenv("POSTGRES_DB", "django"),
        #"USER": os.getenv("POSTGRES_USER", "django"),
        #"PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
        #"HOST": os.getenv("DB_HOST", ""),
        #"PORT": os.getenv("DB_PORT", 5432),
    #}
#}


LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'collected_static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Убрать при деплое
CORS_ORIGIN_WHITELIST = [
    'https://localhost:3000',
]

CORS_ORIGIN_ALLOW_ALL = True
