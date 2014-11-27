# -*- coding: utf-8 -*-

from datetime     import datetime
from dateutil     import rrule
from django.db    import models
from django.utils import timezone

from client.functions import normalize_time

from django.utils.translation import ugettext_lazy as _

class Schedule(models.Model):    
    destination  = models.CharField(max_length=1024)
    initial_time = models.DateTimeField(verbose_name=_("initial datetime"), default=timezone.now())
    rule         = models.ForeignKey('RRule',
                                      null=True,
                                      blank=True,
                                      verbose_name=_("recurrence"),
                                      help_text=_("Selecione '----' para um evento nao recorrente."))
    active       = models.BooleanField(default=True, verbose_name=_("active"))
    
    class Meta:
        app_label = 'client'
    
    def __unicode__(self):
        return u"%(destination)s%(rule)s@ %(initial_time)s" % {
            'destination' : self.destination,
            'rule'        : u' (%s) ' % self.rule if self.rule else ' ',
            'initial_time': datetime.strftime(
                                timezone.localtime(self.initial_time),
                                '%H:%M' if self.rule else '%d/%m/%Y %H:%M'
                            )
        }
    
    def save(self, *args, **kwargs):
        self.initial_time = normalize_time(self.initial_time)
        return super(Schedule, self).save(*args, **kwargs)
    
    def last_runtime(self):
        return self.last_runtime_before_or_equal(timezone.now())
    
    def next_runtime(self):
        return self.next_runtime_after(timezone.now())
    
    def last_runtime_before_or_equal(self, dt):
        if self.rule is not None:
            return self.get_rule().before(normalize_time(dt), True)
        else:
            if self.initial_time <= dt:
                return self.initial_time
            else:
                return None
            
    def next_runtime_after(self, dt):
        print self.rule
        if self.rule is not None:
            return self.get_rule().after(normalize_time(dt), False)
        else:
            if self.initial_time > dt:
                return self.initial_time
            else:
                return None
    
    def is_runtime(self, dt):
        last_runtime_before_or_equal = self.last_runtime_before_or_equal(dt)
        if last_runtime_before_or_equal is None:
            return False
        
        return normalize_time(dt) == last_runtime_before_or_equal
        
    def get_rule(self):
        if self.rule is not None:
            p = {
                'dtstart' : self.initial_time,
                'byhour'  : self.initial_time.hour,
                'byminute': self.initial_time.minute,
            }
            params = self.rule.get_params()
            params.update(p)
            frequency = 'rrule.%s' % self.rule.frequency
            return rrule.rrule(eval(frequency), **params)
