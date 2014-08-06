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

from datetime import datetime, timedelta
#rom django.utils.timezone import utc
from django.conf import settings

#from django.core.files import File

import os

PATH='/Users/gustavo/'
#PATH='/home/gustavo.azevedo/Projects/'

# Create your tests here.
class RuleCase(TestCase):
    
    def setUp(self):
        self.daily_rule = RRule(name=u'diário',
                                description=u'uma vez por dia',
                                frequency=RRule.DAILY)
        self.daily_rule.save()
        
        self.now = datetime.now()
        self.now -= timedelta(seconds=self.now.second) + timedelta(microseconds=self.now.microsecond)
        params = {
            'schedule_time': self.now + timedelta(hours=1),
            'rule': self.daily_rule,
        }
        self.schedule = Schedule(**params)
        self.schedule.save()
        
    def test_rule_ok(self):
        rule = RRule.objects.get(name=u'diário')
        self.assertEqual(rule, self.daily_rule)
        
    def test_schedule_time(self):
        self.assertEqual(self.schedule.schedule_time, self.now + timedelta(hours=1))
    
    def test_schedule_filter_by_time(self):
        schedules = Schedule.objects.filter(schedule_time__hour=self.schedule.schedule_time.hour,
                                           schedule_time__minute=self.schedule.schedule_time.minute)
        self.assertIn(self.schedule, schedules)
    
    def test_next_run(self):
        time = self.now + timedelta(hours=2)
        self.assertEqual(self.schedule.next_run(time), self.now + timedelta(days=1, hours=1))
    
    
    def test_trigger(self):
        time = self.now + timedelta(hours=1)
        self.assertTrue(self.schedule.trigger(time))
    

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