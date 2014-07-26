# -*- coding: utf-8 -*-

from datetime            import datetime, timedelta
from requests.exceptions import ConnectionError
from django.db           import models
from django.conf         import settings
from .constants          import TIMEDELTA_CHOICES, GET, POST
from .functions          import json_request

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
        

class Destination(models.Model):
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
            destinations = WebServer.get().destinations(origin_id).get('destinations', None)
        except ConnectionError: 
            return #retorna silenciosamente (considera os destinos já cadastrados)
        
        #define quais destinations podem ser deletados
        dests_to_delete = [d for d in Destination.objects.exclude(name__in=destinations)
                            if not any(s.destination == d for s in Schedule.objects.all())]
        for dest in dests_to_delete:
            dest.delete()
        #coleta todos os destinations ainda não cadastrados
        dests_to_add = [dn for dn in destinations
                      if not any(dn == d.name for d in Destination.objects.all())]
        for dn in dests_to_add:
            Destination.objects.create(name=dn)

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
    name   = models.CharField(max_length=80,
                              verbose_name=u"nome")
    apikey = models.TextField(verbose_name = u"chave API",
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
        (FINISHED     , u'Backup finalizado.')
        (REMOVED_LOCAL, u'Cópia local removida. Restauro apenas online.')
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
    local_file= models.FileField(null=True)
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
            import sys, traceback
            
            error_type, error, tb = sys.exc_info()
            self.state = self.ERROR_RUNNING
            
                
    def update_error(self, exc_info):
        error_type, error, tb = info
        self.last_error = \
            """
               %(error_type)s: %(error)s
               ==============
               %(traceback)s
            """ % {
                    'error_type': error_type,
                    'error'     : error,
                    'traceback' : tb
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
            self.state = self.ERROR_SENDING
        
        return None
    
class Schedule(models.Model):
    
    TIMEDELTA_CHOICES = (
        (  86400, 'dia(s)'),
        ( 604800, 'semana(s)'),
        (1209600, 'quinzena(s)'),
    )
    destination    = models.ForeignKey('Destination', null=True)
    interval_hours = models.PositiveIntegerField(verbose_name='periodicidade')
    schedule_time  = models.DateTimeField()
    last_scheduled = models.DateTimeField(editable=False)
    last_backup    = models.DateTimeField(auto_now=True,
                                          verbose_name=u'data do último backup')
    def __unicode__(self):
        return u"%s a cada %s" % (self.destination.name, self.interval_str)
    
    #@property
    #def interval_tuple(self):
    #    empty = (0, 0)
    #    return next(((self.interval_hours / div, div)
    #             for div,name in reversed(TIMEDELTA_CHOICES)
    #             if self.interval_hours % div == 0)
    #             , empty)
    
    @property
    def interval_str(self):
        empty = (0, u"")
        return u"%i %s" % next(((self.interval_hours / div, name)
                        for div,name in reversed(self.TIMEDELTA_CHOICES)
                        if self.interval_hours % div == 0),
                        empty)
    @property
    def next_scheduled(self):
        return self.last_scheduled + timedelta(hours=self.interval_hours) \
               if self.last_scheduled \
               else self.schedule_time
    
    @property
    def whole_periods_off(self):
        return (datetime.now()
                - self.last_backup
                + timedelta(hours=self.interval_hours)) / self.interval_hours
        
    def save(self, *args, **kwargs):
        if datetime.now() >= self.next_scheduled:
            self.last_scheduled = self.next_scheduled 
        return super(Schedule, self).save(*args, **kwargs)
    

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
    
