from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# dev atabase
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
