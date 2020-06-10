"""
Django settings for alvisarrentas project.
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# APP CONFIG
DEBUG = True

SECRET_KEY = '!+!gj0u#7rd#@dfe6wn%(1wq(f*afmdqsitd5ag5$=6^%b5)_('

ALLOWED_HOSTS = []

ROOT_URLCONF = 'alvisarrentas.urls'

WSGI_APPLICATION = 'alvisarrentas.wsgi.application'

DEFAULT_CHARSET = 'utf-8'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_celery_results',
    'django_celery_beat',
    'django_tables2',
    'django_filters',
    'bootstrap3',
    'webapp',
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

# DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# LOCALIZATION
LANGUAGE_CODE = 'es-mx'

TIME_ZONE = 'America/Mexico_City'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# FILES
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

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

# AUTHENTICATION
PASSWORD_RESET_TIMEOUT_DAYS = 1

LOGIN_REDIRECT_URL = '/'

LOGIN_URL = '/users/login/'

LOGOUT_REDIRECT_URL = '/users/login/'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
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

# SESSION
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

SESSION_COOKIE_AGE = 1209600  # 2 Weeks

# CELERY
# CELERY_BROKER_URL = 'redis://broker:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Mexico_City'
CELERY_RESULT_BACKEND = 'django-db'


# CFDI
PATH_XLST = os.path.join(BASE_DIR, 'webapp/tools/xslt/cadenaoriginal_3_3.xslt')

PAC_URL = 'http://services.test.sw.com.mx/cfdi33/stamp/v3/'

PAC_TOKEN = 'T2lYQ0t4L0RHVkR4dHZ5Nkk1VHNEakZ3Y0J4Nk9GODZuRyt4cE1wVm5tbXB3YVZxTHdOdHAwVX' \
            'Y2NTdJb1hkREtXTzE3dk9pMmdMdkFDR2xFWFVPUXpTUm9mTG1ySXdZbFNja3FRa0RlYURqbzdz' \
            'dlI2UUx1WGJiKzViUWY2dnZGbFloUDJ6RjhFTGF4M1BySnJ4cHF0YjUvbmRyWWpjTkVLN3ppd3' \
            'RxL0dJPQ.T2lYQ0t4L0RHVkR4dHZ5Nkk1VHNEakZ3Y0J4Nk9GODZuRyt4cE1wVm5tbFlVcU92Y' \
            'UJTZWlHU3pER1kySnlXRTF4alNUS0ZWcUlVS0NhelhqaXdnWTRncklVSWVvZlFZMWNyUjVxYUF' \
            'xMWFxcStUL1IzdGpHRTJqdS9Zakw2UGRiMTFPRlV3a2kyOWI5WUZHWk85ODJtU0M2UlJEUkFTV' \
            'XhYTDNKZVdhOXIySE1tUVlFdm1jN3kvRStBQlpLRi9NeWJrd0R3clhpYWJrVUMwV0Mwd3FhUXd' \
            'pUFF5NW5PN3J5cklMb0FETHlxVFRtRW16UW5ZVjAwUjdCa2g0Yk1iTExCeXJkVDRhMGMxOUZ1Y' \
            'WlIUWRRVC8yalFTNUczZXdvWlF0cSt2UW0waFZKY2gyaW5jeElydXN3clNPUDNvU1J2dm9weHB' \
            'TSlZYNU9aaGsvalpQMUxrSkhlVUY2aXpLNWZkaHZlcDFtMWFhWkJpdGFxSFpRMXZSWUp5QUZsa' \
            'lZWd2huVWx3NUM3dVF6aWxJaGJqUU9QbFdWZW0zMTQxTmd6dUJ3dHR0SDlvTjhLUzFoT3VsMnR' \
            'XWFlTWGFOUDNaeEhmUklFOWVEZjB6OE9QVGhzWnZ1bjRzWkUyeWd3UXlFMUtENVRXQ1pxRjg9.' \
            '6Us1aA5VkXQTHyEBeaq-98l_5NTADHRAayJXQPT9qIA'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FROM_EMAIL = 'facturarentaautmatica<noreply@example.com>'
SERVER_EMAIL = 'facturarentaautmatica<noreply@example.com>'


# TENANT
TENANT_RFC = 'LAN7008173R5'

TENANT_EMAIL = 'noreply@example.com'

RFC = 'LAN7008173R5'

RAZON_SOCIAL = 'Pruebas facturarentaautmatica'

REGIMEN_FISCAL = '601'

CODIGO_POSTAL = '93620'

MONEDA = 'MXN'

SERIE = 'A'

SERIE_REP = 'P'

CLAVE_PROD_SERV = '80131502'

CLAVE_UNIDAD = 'E48'

CSD_CER = os.path.join(BASE_DIR, 'csd/CSD_Pruebas_CFDI_LAN7008173R5.cer')

CSD_KEY = os.path.join(BASE_DIR, 'csd/CSD_Pruebas_CFDI_LAN7008173R5.pem.key')

CSD_PAS = '12345678a'

try:
    from local_settings import *
except ImportError:
    pass
