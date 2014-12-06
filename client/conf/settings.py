
from django.conf import settings

POST = 'POST'
GET  = 'GET'

TBACKUP_DATETIME_FORMAT = getattr(settings, 'TBACKUP_DATETIME_FORMAT', '%Y%m%d%H%M')

WEBSERVER_NAME = getattr(settings, 'WEBSERVER_NAME','WebServer')
WEBSERVER_URL = getattr(settings, 'WEBSERVER_URL','http://127.0.0.1:7000')
WEBSERVER_API_URL = getattr(settings, 'WEBSERVER_API_URL','/api')
WEBSERVER_API_VERSION = getattr(settings, 'WEBSERVER_API_VERSION','v1')