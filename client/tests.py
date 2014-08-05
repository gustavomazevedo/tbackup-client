# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test import Client
from .models import (
    Origin,
    Destination,
    Schedule,
    WebServer,
    RRule,
)

#from datetime import datetime
#rom django.utils.timezone import utc
from django.conf import settings

#from django.core.files import File

import os

PATH='/Users/gustavo/'
#PATH='/home/gustavo.azevedo/Projects/'

# Create your tests here.
class RuleCase(TestCase):
    
    def test_create_rule(self):
        rule = RRule(name=u'diário',
                     description=u'uma vez por dia',
                     frequency=RRule.DAILY)
        rule.save()
        
        

class DestinationCase(TestCase):
    pass
    #def setUp(self):
    #    ws = WebServer.objects.create(
    #        name=settings.WEBSERVER_NAME,
    #        url=settings.WEBSERVER_URL,
    #        api_url=settings.WEBSERVER_API_URL,
    #        api_version=settings.WEBSERVER_API_VERSION
    #    )
    #    
    #    o = Origin.objects.create(
    #        name='Gustavo',
    #    )
    #    
    #def test_loadDestination(self):
    #    Destination.update()
    #    for d in Destination.objects.all():
    #        print name
    #    
    #def test_register(self):
    #    Destination.update()
    #    Origin.register()
    #    
    #    WebServer.get().backup(
    #        {
    #            ''
    #        }
    #    )
    #    
    #    
    #def test_backup(self):
    #    Destination.update()
    #    Origin.register()
    #    
    #    fn2 = os.path.join(PATH, 'virtualenv-1.11.4.tar.gz')
    #    django_file = File(open(fn2, 'rb'))
    #    
    #    