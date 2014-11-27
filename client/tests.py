# -*- coding: utf-8 -*-

from django.test import TestCase
#from django.test import Client
from django.utils import timezone

from .models import (
#    Origin,
#    Destination,
    Schedule,
#    WebServer,
    RRule,
)

from datetime import timedelta
#rom django.utils.timezone import utc
#from django.conf import settings

#from django.core.files import File

#import os

PATH='/Users/gustavo/'
#PATH='/home/gustavo.azevedo/Projects/'

# Create your tests here.
class RuleCase(TestCase):
    fixtures = ['rules.json']
    
    def setUp(self):
        self.daily_rule = RRule(name=u'diário',
                                description=u'uma vez por dia',
                                frequency=RRule.DAILY)
        self.daily_rule.save()
        
        self.now = timezone.now()
        self.now -= timedelta(seconds=self.now.second) + timedelta(microseconds=self.now.microsecond)
        params = {
            'initial_time': self.now + timedelta(hours=1),
            'rule': self.daily_rule,
        }
        self.schedule = Schedule(**params)
        self.schedule.save()
        
    def test_rule_ok(self):
        #print [r for r in RRule.objects.all()]
        rule = RRule.objects.get(name=u'diário')
        self.assertEqual(rule, self.daily_rule)
        
    def test_initial_time(self):
        self.assertEqual(self.schedule.initial_time, self.now + timedelta(hours=1))
    
    def test_schedule_filter_by_time(self):
        print self.schedule.initial_time
        print (self.schedule.initial_time.hour, self.schedule.initial_time.minute)
        ss = Schedule.objects.all()
        for s in ss:
            print s.initial_time
            print (s.initial_time.hour, s.initial_time.minute)
            print (s.initial_time.hour == self.schedule.initial_time.hour and
                  s.initial_time.minute == self.schedule.initial_time.minute)
            print s.initial_time == self.schedule.initial_time      

        #schedules = Schedule.objects.filter(initial_time__hour=self.schedule.initial_time.hour,
        #                                   initial_time__minute=self.schedule.initial_time.minute)
        schedules = Schedule.objects.filter(initial_time=self.schedule.initial_time)
        self.assertIn(self.schedule, schedules)
    
    def test_next_runtime(self):
        time = self.now + timedelta(hours=2)
        self.assertEqual(self.schedule.next_runtime_after(time), self.now + timedelta(days=1, hours=1))
    
    
    def test_is_runtime(self):
        time = self.now + timedelta(hours=1)
        self.assertTrue(self.schedule.is_runtime(time))
    

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
    #    WebServer.instance().backup(
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