# -*- coding: utf-8 -*-
import json
import urllib
import urllib2
import requests

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
    def update():
        #try:
        destinations = WebServer.get().destinations().get('destinations', None)
        #except:
        #    return
        
        #dn_array = [d[u"name"] for d in destination_names_server]
        #print dn_array
        print destinations
        #coleta todos os destinations não contidos no array que não estejam
        #sendo utilizados em alguma config
        dests_to_delete = [d for d in Destination.objects.exclude(name__in=destinations)
                            if not any(c.destination == d for c in Config.objects.all())]
        print dests_to_delete
        for dest in dests_to_delete:
            dest.delete()
        #coleta todos os nomes de destinations ainda não cadastrados
        dns_to_add = [dn for dn in destinations
                      if not any(dn == d.name for d in Destination.objects.all())]
        for dn in dns_to_add:
            print u"add " + dn
            Destination.objects.create(name=dn)

class Origin(models.Model):
    name = models.CharField(max_length=1024,
                            verbose_name=u"nome")
    #registered = models.BooleanField(default=False,
    #                                 editable=False,
    #                                 verbose_name=u'registrado')
    
    class Meta:
        verbose_name = u"origem"
        verbose_name_plural = u"origem"
    
    def __unicode__(self):
        return self.name
    
    @staticmethod
    def register(name):
        try:
            return WebServer.get().register(name)
        except:
            return None
        

class WebServer(models.Model):
    name   = models.CharField(max_length=80,
                              verbose_name=u"nome")
    apikey = models.TextField(verbose_name = u"chave",
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
    
    def destinations(self, origin_id, apikey):
        return self.remote_action(u"destinations",
                                  GET,
                                  origin_id,
                                  get_signed_data(None, apikey))
        
    def register(self, origin_name):
        #import ipdb; ipdb.set_trace()
        return self.remote_action(u"register_origin",
                                  POST,
                                  get_signed_data(
                                    {u"origin": origin_name},
                                    settings.R_SIGNATURE_KEY,
                                    ))
    
    def backup(self, origin_id, apikey, data, files):
        return self.remote_action(u"backup",
                                  POST,
                                  origin_id,
                                  get_signed_data(data, apikey),
                                  files)
    
    def restore(self, origin_id, apikey, data):
        return self.remote_action(u"restore",
                                  POST,
                                  origin_id,
                                  get_signed_data(data, apikey))
    
    def remote_action(self, view_name, origin_id=None, method=None, data=None, files=None):
        return self._json_request(
            url =u"%s/server/%s%s/" %
            (
                self.url,
                origin_id + u"/" if origin_id else u"",
                view_name
            ),
            method=method,
            data=data,
            files=files
        )
    
    def _json_request(self, url, method=None, data=None, files=None):
        if method == POST:
            r = requests.post(url, data=data, files=files)
        else:
            r = requests.get(url, params=data)
            
        print r
        print r.status_code
        json_response = r.json()
        print json_response
        if r.status_code == 200:
            if authenticated(json_response):
                import ipdb; ipdb.set_trace()
                return remove_key(json_response, u"signature")
            else:
                import ipdb; ipdb.set_trace()
                from django.http import HttpResponse
                return HttpResponse(u"<h1>Erro de autenticação</h1><h2>Assinatura não válida</h2>")
        else:
            import ipdb; ipdb.set_trace()
            return {}

from Crypto.Hash import SHA
import operator
from datetime import datetime

def authenticated(fulldata):
    import ipdb; ipdb.set_trace()
    signature = fulldata.get(u"signature", None)
    data = remove_key(fulldata, u"signature")
    import ipdb; ipdb.set_trace()
    if not signature:
        return False
    apikey = WebServer.get().apikey
    import ipdb; ipdb.set_trace()
    if apikey:
        import ipdb; ipdb.set_trace()
        return signature == sign(data, apikey)
    else:
        import ipdb; ipdb.set_trace()
        return signature == sign(data, settings.R_SIGNATURE_KEY)
    
def sign(data, key):
    sha1 = SHA.new()
    if not data:
        sha1.update(u"None")
    else:
        sorted_data = sorted(data.iteritems(),key=operator.itemgetter(0))
        for item in sorted_data:
            sha1.update(unicode(item))
    sha1.update(key)
    
    import ipdb; ipdb.set_trace()
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
        i = ''
        n = ''
        for div, name in reversed(TIMEDELTA_CHOICES):
            if self.interval % div == 0:
                i = str(self.interval / div)
                n = name if i != '1' else name[0:-1]
                break
        return u"%s %s" % (i, n)

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
    
