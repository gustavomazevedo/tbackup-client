# -*- coding: utf-8 -*-

from datetime                 import datetime, timedelta
from requests.exceptions      import ConnectionError
from dateutil                 import rrule
from django.db                import models
from django.conf              import settings
from django.utils.translation import ugettext_lazy as _
from .constants               import GET, POST
from .functions               import json_request

# Create your models here.
#class Destination(NameableMixin):
#    
#    class Meta:
#        abstract = True
#    
#
#class Origin(NameableMixin):
#    pass
#    
#    
#class Server(models.Model):
#    url = models.CharField(max_length=1024,
#                           blank=True,
#                           null=True)
#    
#    @staticmethod
#    def get_server():
#        return Server.objects.get(pk=1)
#    
#    def send_(self, ):
#        pass
#    
#
#class Backup(models.Model):
#    pass
#
#
#
#    
#class BackupQueue(LoggableMixin):
#    origin = models
#    
#    @staticmethod
#    def pop():
#        pass
#    
#    @staticmethod
#    def push(obj):
#        pass
#    
#    @staticmethod
#    def send(obj):
   
class RRule(models.Model):
    """
    Adapted from django-schedule project:
    https://github.com/thauber/django-schedule
    
    This defines a rule by which an event will recur.  This is defined by the
    rrule in the dateutil documentation.

    * name - the human friendly name of this kind of recursion.
    * description - a short description describing this type of recursion.
    * frequency - the base recurrence period
    * param - extra params required to define this type of recursion. The params
      should follow this format:

        param = [rruleparam:value;]*
        rruleparam = see list below
        value = int[,int]*

      The options are: (documentation for these can be found at
      http://labix.org/python-dateutil#head-470fa22b2db72000d7abe698a5783a46b0731b57)
        ** count
        ** bysetpos
        ** bymonth
        ** bymonthday
        ** byyearday
        ** byweekno
        ** byweekday
        ** byhour
        ** byminute
        ** bysecond
        ** byeaster
    """
    YEARLY  = 'YEARLY'
    MONTHLY = 'MONTHLY' 
    WEEKLY  = 'WEEKLY'  
    DAILY   = 'DAILY'   
    HOURLY  = 'HOURLY'  
    MINUTELY= 'MINUTELY'
    SECONDLY= 'SECONDLY'
    
    FREQUENCIES = (
        (YEARLY  , _('Yearly')),
        (MONTHLY , _('Monthly')),
        (WEEKLY  , _('Weekly')),
        (DAILY   , _('Daily')),
        (HOURLY  , _('Hourly')),
        (MINUTELY, _('Minutely')),
        (SECONDLY, _('Secondly')),
    )
    name = models.CharField(_("name"), max_length=32)
    description = models.TextField(_("description"))
    frequency = models.CharField(_("frequency"),
                                 choices=FREQUENCIES,
                                 max_length=10)
    params = models.TextField(_("params"), null=True, blank=True)

    class Meta:
        verbose_name = _('rule')
        verbose_name_plural = _('rules')

    def get_params(self):
        """
        >>> rule = RRule(params = "count:1;bysecond:1;byminute:1,2,4,5")
        >>> rule.get_params()
        {'count': 1, 'byminute': [1, 2, 4, 5], 'bysecond': 1}
        """
        if self.params is None:
            return {}
        params = self.params.split(';')
        param_dict = []
        for param in params:
            param = param.split(':')
            if len(param) == 2:
                param = (str(param[0]),
                           [int(p) for p in param[1]
                                            .translate(None, '()[]')
                                            .split(',')])
                if len(param[1]) == 1:
                    param = (param[0], param[1][0])
                param_dict.append(param)
        return dict(param_dict)

    def __unicode__(self):
        """Human readable string for Rule"""
        return self.name

     

class Destination(models.Model):
    """
    """
    name = models.CharField(max_length=1024,
                            verbose_name=u"nome",
                            primary_key=True)

    class Meta:
        verbose_name = u"destino"
        ordering = [u"name"]

    def __unicode__(self):
        return self.name

    @staticmethod
    def update(origin_id):
        try:
            destinations = WebServer.get() \
                           .destinations(origin_id) \
                           .get('destinations', None)
        except ConnectionError: 
            return #retorna silenciosamente (considera os destinos já cadastrados)

        #define quais destinations podem ser deletados
        dests_to_delete = [
            d
            for d in Destination.objects.exclude(name__in=destinations)
            if not any(s.destination == d for s in Schedule.objects.all())
        ]
        for dest in dests_to_delete:
            dest.delete()
        #coleta todos os destinations ainda não cadastrados
        dests_to_add = [
            dn
            for dn in destinations
            if not any(dn == d.name for d in Destination.objects.all())
        ]
        for destname in dests_to_add:
            Destination.objects.create(name=destname)

class Origin(models.Model):
    name = models.CharField(max_length=1024,
                            verbose_name=u"nome")
    #registered = models.BooleanField(default=False,
    #                                 editable=False,
    #                                 verbose_name=u'registrado')
    remote_id = models.BigIntegerField(editable=False)

    class Meta:
        verbose_name = u"origem"
        verbose_name_plural = u"origem"

    def __unicode__(self):
        return self.name

    @staticmethod
    def get():
        return Origin.objects.filter(pk=1) or None

    @staticmethod
    def register(name):
        return WebServer.get().register(name)

    @staticmethod
    def check_availability(name):
        return WebServer.get().check_availability(name)

class WebServer(models.Model):
    name        = models.CharField(max_length=80,
                                   verbose_name=u"nome")
    apikey      = models.TextField(verbose_name=u"chave API",
                              editable=False)
    url         = models.CharField(max_length=1024)
    api_url     = models.CharField(max_length=1024)
    api_version = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = u"web server"

    @staticmethod
    def get():
        #import ipdb; ipdb.set_trace()
        try:
            return WebServer.objects.get(pk=1)
        except WebServer.DoesNotExist:
            return WebServer.objects.create(
                name=settings.WEBSERVER_NAME,
                url=settings.WEBSERVER_URL,
                api_url=settings.WEBSERVER_API_URL,
                api_version=settings.WEBSERVER_API_VERSION
            )

    def check_availability(self, origin_name):
        #import ipdb; ipdb.set_trace()
        return self.remote_action(view_name= u"origin_available",
                                  method   = GET,
                                  data     = {u"origin": origin_name})
    
    def register(self, origin_name):
        #import ipdb; ipdb.set_trace()
        return self.remote_action(view_name= u"register_origin",
                                  method   = POST,
                                  data     = {u"origin": origin_name})
    
    def destinations(self, origin_id):
        return self.remote_action(view_name= u"destinations",
                                  method   = GET,
                                  apikey   = self.apikey,
                                  origin_id= origin_id)
    
    def backup(self, origin_id, data, files):
        return self.remote_action(view_name= u"backup",
                                  method   = POST,
                                  data     = data,
                                  apikey   = self.apikey,
                                  origin_id= origin_id,
                                  files    = files)
    
    def restore(self, origin_id, data):
        return self.remote_action(view_name= u"restore",
                                  method   = POST,
                                  data     = data,
                                  apikey   = self.apikey,
                                  origin_id= origin_id)
    
    def remote_action(self, view_name, method=None, data=None,
                      apikey=None,
                      origin_id=None, files=None):
        return json_request(
            url   =u"%(address)s/server/%(id)s%(view)s/" %
                   {
                     'address': self.url,
                     'id'     : u"%i/" % origin_id if origin_id else u"",
                     'view'   : view_name
                   },
            method=method,
            data  =data,
            apikey=apikey,
            files =files
        )
    

#class Plan(models.Model):
#    destination = models.ForeignKey('Destination')
#    interval    = models.IntegerField(verbose_name='periodicidade')
#    last_backup = models.DateTimeField(auto_now=True,verbose_name=u'data do último backup')
#    
#    def __unicode__(self):
#        return self.destination.name + unicode(self.interval)
class LocalBackupQueue(models.Model):
    
    def queue(self, ):
        pass
    
    def dequeue(self, ):
        pass
    
    @staticmethod
    def empty():
        pass
    
def get_path_name(instance, filename):
    return u'/'.join([instance.schedule.destination.name, filename])
    
class Backup(models.Model):
    IDLE          = 'ID'
    RUNNING       = 'RU'
    ERROR_RUNNING = 'ER'
    WAITING       = 'WA'
    SENDING       = 'SE'
    ERROR_SENDING = 'ES'
    FINISHED      = 'FI'
    REMOVED_LOCAL = 'RL'
    STATE_CHOICES = (
        (IDLE         , u'Não Iniciado.'),
        (RUNNING      , u'Executando backup local.'),
        (ERROR_RUNNING, u'Erro ao tentar executar o backup local.'),
        (WAITING      , u'Aguardando para enviar.'),
        (SENDING      , u'Enviando para servidor.'),
        (ERROR_SENDING, u'Erro ao tentar enviar para servidor.'),
        (FINISHED     , u'Backup finalizado.'),
        (REMOVED_LOCAL, u'Cópia local removida. Restauro apenas online.'),
    )
    SCHEDULED     = 'S'
    EXTRAORDINARY = 'E'
    KIND_CHOICES = (
        (SCHEDULED    , 'Agendado'),
        (EXTRAORDINARY, 'Especial'),
    )
    schedule  = models.ForeignKey('Schedule')
    time      = models.DateTimeField()
    local_name= models.CharField(max_length=256)
    local_file= models.FileField(upload_to=get_path_name,
                                 null=True)
    size      = models.BigIntegerField()
    destination_name = models.CharField(max_length=256)
    kind = models.CharField(max_length=1,
                            choices=KIND_CHOICES,
                            default='A')
    state = models.CharField(max_length=2,
                             choices=STATE_CHOICES,
                             default='I')
    last_error = models.TextField(null=True)
    
    
    def advance_state(self):
        if self.state == self.IDLE:
            self.state = self.RUNNING
        elif self.state == self.RUNNING:
            self.state = self.WAITING
        elif self.state == self.WAITING:
            self.state = self.SENDING
        elif self.state == self.SENDING:
            self.state = self.FINISHED
        elif self.state == self.FINISHED:
            self.state = self.REMOVED_LOCAL
        else:
            #raise Exception('State: %s. Cannot advance state.' % self.state)
            return
            
    
    def run_local_backup(self, ):
        if self.ERROR_RUNNING:
            self.state = self.IDLE
        if self.state != self.IDLE:
            #raise Exception('State: %s. Cannot run local backup.' % self.state)
            return
        self.advance_state()
        try:
            pass
            self.advance_state()
        except:
            import sys
            self.update_error(sys.exc_info())
            self.state = self.ERROR_RUNNING
            
                
    def update_error(self, exc_info):
        exc_type, exc_value, exc_traceback = exc_info
        self.last_error = \
            """
               %(type)s: %(value)s
               ==============
               %(traceback)s
            """ % {
                    'type'     : exc_type,
                    'value'    : exc_value,
                    'traceback': exc_traceback,
                  }
        
    def send(self, ):
        if self.ERROR_SENDING:
            self.state = self.WAITING
        if self.state != self.WAITING:
            #raise Exception('State: %s. Cannot send backup' % self.state)
            return
            
        self.advance_state()
        try:
            pass
            self.advance_state()
        except:
            import sys
            self.update_error(sys.exc_info())
            self.state = self.ERROR_SENDING
        
        return None
    
class Schedule(models.Model):
    
    TIMEDELTA_CHOICES = (
        (  86400, 'dia(s)'),
        ( 604800, 'semana(s)'),
        (1209600, 'quinzena(s)'),
    )
    destination    = models.ForeignKey('Destination', null=True)
    schedule_time  = models.DateTimeField()
    rule           = models.ForeignKey('RRule',
                                       null=True,
                                       blank=True,
                                       verbose_name=_("rule"),
                                       help_text=_("Selecione '----' para um evento não recorrente."))
    
    def __unicode__(self):
        return u"%s a cada %s" % (self.destination.name, self.interval_str)
    
    
    def rem_seconds(self, dt):
        return dt - timedelta(seconds=dt.second) - timedelta(microseconds=dt.microsecond)
    
    def last_run(self):
        return self.last_before(datetime.now())
    
    def next_run(self):
        return self.next_after(datetime.now())
    
    def last_before(self, dt):
        if self.rule is not None:
            return self.get_rule().before(self.rem_seconds(dt), True)
        else:
            if self.scheduled_time <= now:
                return self.scheduled_time
            else:
                return None
            
    def next_after(self, dt):
        if self.rule is not None:
            return self.get_rule().after(self.rem_seconds(dt), False)
        else:
            if self.scheduled_time > dt:
                return self.scheduled_time
            else:
                return None
    
    def trigger(self, dt):
        last_before = self.last_before(dt)
        if last_before is None:
            return False
        return self.rem_seconds(dt) == last_before
    
    
    def get_rule(self):
        if self.rule is not None:
            p = {
                'dtstart' : self.schedule_time,
                'byhour': self.schedule_time.hour,
                'byminute': self.schedule_time.minute,
            }
            params = self.rule.get_params()
            params.update(p)
            frequency = 'rrule.%s' % self.rule.frequency
            return rrule.rrule(eval(frequency), **params)
        
    #@property
    #def interval_tuple(self):
    #    empty = (0, 0)
    #    return next(((self.interval_hours / div, div)
    #             for div,name in reversed(TIMEDELTA_CHOICES)
    #             if self.interval_hours % div == 0)
    #             , empty)
    
    #@property
    #def interval_str(self):
    #    empty = (0, u"")
    #    return u"%i %s" % next(((self.interval_hours / div, name)
    #                    for div,name in reversed(self.TIMEDELTA_CHOICES)
    #                    if self.interval_hours % div == 0),
    #                    empty)
    #@property
    #def next_scheduled(self):
    #    return self.last_scheduled + timedelta(hours=self.interval_hours) \
    #           if self.last_scheduled \
    #           else self.schedule_time
    #
    #@property
    #def whole_periods_off(self):
    #    return (datetime.now()
    #            - self.last_backup
    #            + timedelta(hours=self.interval_hours)) / self.interval_hours
    #    
    #def save(self, *args, **kwargs):
    #    if datetime.now() >= self.next_scheduled:
    #        self.last_scheduled = self.next_scheduled 
    #    return super(Schedule, self).save(*args, **kwargs)
    

class BackupStatus(models.Model):
    executing = models.BooleanField(default=False)
    count = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = 'backup status'
        
    def save(self, *args, **kwargs):
        '''
        A cada 60 execuções (= 1 hora) que se passam com executing = True,
        reseta-o para False, para prevenir que uma queda do servidor prenda
        o status em True indefinidamente.
        '''
        if self.executing:
            self.count += 1
        else:
            self.count = 0
            
        if self.count >= 60:
            self.count = 0
            self.executing = False
        super(BackupStatus, self).save(*args, **kwargs)
    
class Log(models.Model):
    #origin = models.ForeignKey('Origin')
    destination = models.ForeignKey('Destination')
    date = models.DateTimeField(verbose_name='data')
    filename = models.CharField(max_length=1024, verbose_name='arquivo')
    local_status = models.BooleanField() 
    remote_status = models.BooleanField()
    
    def __unicode__(self):
        return self.filename
    
    def restore_link(self):
        if self.remote_status:
            return '<a href="/tbackup_client/restore/%s">Restore<img src="/static/img/Refresh.png"/></a>' % self.id
        return ''
    
    restore_link.short_description = 'Restaurar'
    restore_link.allow_tags = True
    

