# -*- coding: utf-8 -*-
import json
import urllib
import urllib2
import requests

from requests.exceptions import ConnectionError

from django.db import models
from django.conf import settings

from .mixins import NameableMixin, LoggableMixin

POST = 'POST'
GET = 'GET'

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
                            if not any(c.destination == d for c in Config.objects.all())]
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
        return self._json_request(
            url =u"%s/server/%s%s/" %
            (
                self.url,
                u"%i/" % origin_id if origin_id else u"",
                view_name
            ),
            method=method,
            data=data,
            apikey=apikey,
            files=files
        )
    
    def _json_request(self, url, method=None, data=None, apikey=None, files=None):
        signed_data = get_signed_data(data, apikey)
        if method == POST:
            #import ipdb; ipdb.set_trace()
            r = requests.post(url, data=signed_data, files=files)
        else:
            #import ipdb; ipdb.set_trace()
            r = requests.get(url, params=signed_data)
            
        print r
        print r.status_code
        
        if r.status_code != 200:
            #print r.text
            with open('~/Documents/untitled.html', 'wb') as f:
                f.write(r.text)
            return r.text
        json_response = r.json()
        print json_response
        if r.status_code == 200:
            if authenticated(json_response, apikey):
                return remove_key(json_response, u"signature")
            else:
                import ipdb; ipdb.set_trace()
                from django.http import HttpResponse
                return HttpResponse(u"<h1>Erro de autenticação</h1><h2>Assinatura não válida</h2>")
        else:
            #import ipdb; ipdb.set_trace()
            return {}

from Crypto.Hash import SHA
import operator
from datetime import datetime

def authenticated(fulldata, apikey):
    signature = fulldata.get(u"signature", None)
    data = remove_key(fulldata, u"signature")
    if not signature:
        return False
    return signature == sign(data, apikey)
    
def sign(data, apikey=None):
    sha1 = SHA.new()
    if not data:
        sha1.update(u"None")
    else:
        sorted_data = sorted(data.iteritems(),key=operator.itemgetter(0))
        for item in sorted_data:
            sha1.update(unicode(item))
    used_key = apikey or settings.R_SIGNATURE_KEY
    sha1.update(used_key)
    
    #import ipdb; ipdb.set_trace()
    return sha1.hexdigest()

def get_signed_data(data, key):
    return_data = dict(data) if data else {}
    
    return_data[u"timestamp"] = u"%s" % json.dumps(unicode(datetime.now()))
    return_data[u"signature"] = u"%s" % sign(return_data, key)
    
    #import ipdb; ipdb.set_trace()
    return return_data

def remove_key(d, key):
    r = dict(d)
    del r[key]
    return r

#class Plan(models.Model):
#    destination = models.ForeignKey('Destination')
#    interval    = models.IntegerField(verbose_name='periodicidade')
#    last_backup = models.DateTimeField(auto_now=True,verbose_name=u'data do último backup')
#    
#    def __unicode__(self):
#        return self.destination.name + unicode(self.interval)

class Config(models.Model):
    destination = models.ForeignKey('Destination', null=True)
    interval    = models.IntegerField(verbose_name='periodicidade')
    last_backup = models.DateTimeField(auto_now=True,verbose_name=u'data do último backup')
    
    def __unicode__(self):
        return u"%s a cada %s" % (self.destination.name, self.interval_str)
    
    @property
    def interval_str(self):
        from .forms import TIMEDELTA_CHOICES
        empty = (0, u"")
        return u"%i %s" % next(((self.interval / div, name)
                        for div,name in reversed(TIMEDELTA_CHOICES)
                        if self.interval % div == 0),
                        empty)

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
    
