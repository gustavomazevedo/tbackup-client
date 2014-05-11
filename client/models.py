# -*- coding: utf-8 -*-

from django.db import models

from .mixins import NameableMixin, LoggableMixin

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
                            verbose_name=u'nome',
                            primary_key=True)
    
    class Meta:
        verbose_name = u'destino'
        ordering = ['name']
        
    def __unicode__(self):
        return self.name
    
    @staticmethod
    def update():
        destination_names_server = WebServer.objects.get(pk=1).get_resource_list(u'destination')
        dn_array = [d['name'] for d in destination_names_server]
        dests_to_delete = Destination.objects.exclude(name__in=dn_array)
        for d in dests_to_delete:
            d.delete()
        all_dests = Destination.objects.all()
        dests_to_add = (d for d in dn_array if not d.name in all_dests)
        for d in dests_to_add:
            Destination.objects.create(name=d.name)

class Origin(models.Model):
    name = models.CharField(max_length=1024,
                            verbose_name=u'nome')
    
    class Meta:
        verbose_name = u'origem'
        verbose_name_plural = u'origens'
        ordering = ['name']
    
    def __unicode__(self):
        return self.name

class WebServer(models.Model):
    name   = models.CharField(max_length=80,
                              verbose_name=u'nome')
    apikey = models.TextField(verbose_name = u'chave',
                              editable=False)
    api_url     = models.CharField(max_length=1024)
    api_version = models.CharField(max_length=20)
    
    def __unicode__(self):
        return self.name
    
    def get_resource_list(self, resource_name):
        full_url = '%s/%s/%s/?format=json&apikey=' % (self.api_url,
                                                      self.api_version,
                                                      resource_name,
                                                      self.apikey)
        
        response = some_magic_lib.get(full_url)
        if response.code == '200':
            pass
        else:
            pass
    

#class Config(models.Model):
#    destination = models.ForeignKey('Destination')
#    interval    = models.IntegerField(verbose_name='periodicidade')
#    last_backup = models.DateTimeField(default=datetime.now(),verbose_name=u'data do último backup')
#    
#    def __unicode__(self):
#        from .forms import TIMEDELTA_CHOICES
#        i, n = ''
#        #n = ''
#        for div, name in reversed(TIMEDELTA_CHOICES):
#            if self.interval % div == 0:
#                i = str(self.interval / div)
#                n = name if i != '1' else name[0:-1]
#                break
#        return self.destination.name + " a cada " + i + " " + n  
#
#class BackupStatus(models.Model):
#    executing = models.BooleanField(default=False)
#    count = models.IntegerField(default=0)
#    
#    def save(self, *args, **kwargs):
#        '''
#        A cada 60 execuções (= 1 hora) que se passam com executing = True,
#        reseta-o para False, para prevenir que uma queda do servidor prenda
#        o status em True indefinidamente.
#        '''
#        if self.executing:
#            self.count += 1
#        else:
#            self.count = 0
#            
#        if self.count >= 60:
#            self.count = 0
#            self.executing = False
#        super(BackupStatus, self).save(*args, **kwargs)
#    
#class Log(models.Model):
#    #origin = models.ForeignKey('Origin')
#    destination = models.ForeignKey('Destination')
#    date = models.DateTimeField(verbose_name='data')
#    filename = models.CharField(max_length=1024, verbose_name='arquivo')
#    local_status = models.BooleanField() 
#    remote_status = models.BooleanField()
#    
#    def __unicode__(self):
#        return self.filename
#    
#    def restore_link(self):
#        if self.remote_status:
#            return '<a href="/tbackup_client/restore/%s">Restore<img src="/static/img/Refresh.png"/></a>' % self.id
#        return ''
#    restore_link.short_description = 'Restaurar'
#    restore_link.allow_tags = True
#    
