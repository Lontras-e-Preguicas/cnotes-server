from pathlib import Path
from environ import Env
from warnings import warn

BASE_DIR = Path(__file__).resolve().parent.parent

env = Env(
    DEBUG=(bool, False),
    BOTO=(bool, False),
    ALLOWED_HOSTS=(list, []),
)

env.read_env(env_file=str(Path.joinpath(BASE_DIR.parent, '.env')))  # Loads .env file

DEBUG = env('DEBUG')
BOTO = env('BOTO')

SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = env('ALLOWED_HOSTS')

DATABASES = {
    'default': env.db()
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',
    'rest_framework.authtoken',
    'django_cleanup',  # Unused files cleanup
    'drf_yasg',  # OpenAPI Generation
    'storages',
    'core',
    'user',
    'notebook',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cnotes.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cnotes.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'core.User'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Token': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}

# i18n

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static and Media

if DEBUG and not BOTO:
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'

    MEDIA_ROOT = Path.joinpath(BASE_DIR, 'media')
    STATIC_ROOT = Path.joinpath(BASE_DIR, 'staticfiles')
else:
    # S3 settings
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME')
    AWS_S3_ENDPOINT_URL = env('AWS_S3_ENDPOINT_URL')
    AWS_LOCATION = env('AWS_LOCATION', default="")

    # s3 static settings
    STATIC_LOCATION = 'static'
    STATIC_URL = f'https://{AWS_S3_ENDPOINT_URL}/{AWS_LOCATION}/{STATIC_LOCATION}/'
    STATICFILES_STORAGE = 'cnotes.storages.StaticStorage'
    # s3 public media settings
    PUBLIC_MEDIA_LOCATION = 'media'
    MEDIA_URL = f'https://{AWS_S3_ENDPOINT_URL}/{AWS_LOCATION}/{PUBLIC_MEDIA_LOCATION}/'
    DEFAULT_FILE_STORAGE = 'cnotes.storages.PublicMediaStorage'


# E-Mail settings

EMAIL_SUBJECT_PREFIX = '[CNotes] '
SERVER_EMAIL = env('SERVER_EMAIL', default='admin-noreply@localhost')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@localhost')
EMAIL_SSL_KEYFILE = env('EMAIL_SSL_KEYFILE', default=None)
EMAIL_SSL_CERTFILE = env('EMAIL_SSL_CERTFILE', default=None)

# django-environ email_url, might override previous e-mail settings
EMAIL_CONFIG = env.email_url('EMAIL_URL')
vars().update(EMAIL_CONFIG)
