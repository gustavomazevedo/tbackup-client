# -*- coding: utf-8 -*-
import os
import socket

from django.db import models

from client.conf.settings import (
    GET,
    POST,
    WEBSERVER_NAME,
    WEBSERVER_URL,
    WEBSERVER_API_URL,
    WEBSERVER_API_VERSION
)
from client.functions import json_request

class WebServer(models.Model):
    name          = models.CharField(max_length=80,
                                   verbose_name=u"nome")
    apikey        = models.TextField(verbose_name=u"chave API",
                              editable=False)
    url           = models.CharField(max_length=1024)
    api_url       = models.CharField(max_length=1024)
    api_version   = models.CharField(max_length=20)
    active        = models.BooleanField(default=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'client'
        verbose_name_plural = u"web server"
        get_latest_by = 'creation_date'

    @staticmethod
    def get():
        #gets a list of available WebServers, new first
        webservers = WebServer.objects.filter(active=True).order_by('-creation_date')
        #import ipdb; ipdb.set_trace()
        #In case there are no WebServers, create the default one
        if not webservers.exists():
            data = {
                'name'        : WEBSERVER_NAME,
                'url'         : WEBSERVER_URL,
                'api_url'     : WEBSERVER_API_URL,
                'api_version' : WEBSERVER_API_VERSION
            }
            ws = WebServer.objects.create(**data)
            if ws.is_up():
                return ws
        #In case there are already
        else: 
            for ws in webservers:
                #returns the first one which is online
                if ws.is_up():
                    return ws
        #if there are no online, available webservers
        return None

    
    @staticmethod
    def update_ws_info():
        #retrieves WebServer info
        origin = Origin.get()
        try:
            wso = WebServer.objects.get(pk=1)
        except WebServer.DoesNotExist:
            return
        result = wso.remote_action(view_name=u"check_info",
                                  method   = GET,
                                  apikey   = wso.apikey,
                                  origin_id= origin.id)
        webservers = result.get('webservers', None)
        if not webservers:
            return
        for ws in webservers:
            up_to_date = ws.get('up_to_date', None)
            if not up_to_date:
                name        = ws.get('name'       , None)
                url         = ws.get('url'        , None)
                api_url     = ws.get('api_url'    , None)
                api_version = ws.get('api_version', None)
                apikey      = ws.get('apikey'     , None)
                
                #if all values are defined
                if all([name, url, api_url, api_version, apikey]):
                    try:
                       wso = WebServer.objects.get(name=name)
                    except WebServer.DoesNotExist:
                       wso = WebServer(name=name)
                    data = {
                        'url' : url,
                        'api_url': api_url,
                        'api_version': api_version,
                        'apikey': apikey,
                    }   
                    wso.update(**data)
                    wso.save()

    def is_up(self):
        """
        Checks if WebServer is online, by pinging one packet with 2 second tolerance
        If result is different from zero, consider it offline
        """
        hostname = self.url.replace('http://', '').rpartition(':')[0]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        answer = False
        try:
            s.connect((hostname,7000))
            #s.connect((hostname,80))
            answer = True
        except:
            pass
        s.close()
        return answer
        #response = os.system('ping -c 1 -W2 %s > /dev/null 2>&1' % hostname) 
        #if server is up, response will be 0
        #return response == 0
    
    def update(self, url, api_url, api_version, apikey, active):
        self.url = url
        self.api_url = api_url
        self.api_version = api_version
        self.apikey = apikey
        self.active = active
    
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
    
    
