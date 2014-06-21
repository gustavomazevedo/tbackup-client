import os.path
from settings import BASE_DIR

DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY      = '_2q#m6h3qr35t7=+#p1%_wqhr*&(2^g&hbd51z%h_0$!rmbh$9'
R_SIGNATURE_KEY = 'ae+c5l(^@653f-hp_e8s*@l)knb30&s4a#$n&^6^@-o25_*)tz'
# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

WEBSERVER_NAME = 'WebServer'
WEBSERVER_URL = 'http://127.0.0.1:7000'
WEBSERVER_API_URL = '/api'
WEBSERVER_API_VERSION = 'v1'

