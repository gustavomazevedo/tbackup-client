# -*- coding: utf-8 -*-
import os

from datetime                 import datetime
from requests.exceptions      import ConnectionError
from dateutil                 import rrule
from django.db                import models
from django.utils             import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
#from django.conf.settings     import STATIC_URL
from .conf.settings           import (
    DATETIME_FORMAT,
    GET,
    POST,
    WEBSERVER_NAME,
    WEBSERVER_URL,
    WEBSERVER_API_URL,
    WEBSERVER_API_VERSION,
    settings
)
#from .constants               import GET, POST
from .functions               import json_request, normalize_time

# Create your models here.


