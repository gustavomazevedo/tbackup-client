# -*- coding: utf-8 -*-
import os
import socket
import slumber

from django.db import models
from django.utils.translation import gettext_lazy as _

from client.conf.settings import (
    GET,
    POST,
    #WEBSERVER_NAME,
    #WEBSERVER_URL,
    #WEBSERVER_API_URL,
    #WEBSERVER_API_VERSION
)
from client.functions import json_request
from client.auth import HTTPTokenAuth

DEFAULT_TOKEN = None
try:
    from client.default_auth import DEFAULT_TOKEN
except ImportError:
    pass

class WebServer(models.Model):
    name          = models.CharField(max_length=80,
                                     verbose_name=u"nome")
    url           = models.CharField(max_length=1024)
    api_root      = models.CharField(max_length=1024)
    active        = models.BooleanField(default=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'client'
        verbose_name = u"servidor"
        verbose_name_plural = u"servidor"
        get_latest_by = 'creation_date'

    @staticmethod
    def instance():
        #gets a list of available WebServers, new first
        webservers = WebServer.objects.filter(active=True).order_by('creation_date')
        if webservers.count() == 0:
            raise Exception(_('No active WebServer. Please contact administrators'))
        for ws in webservers:
            #returns the first one which is online
            if ws.is_online():
                return ws
        raise Exception(_('There are no online servers at the moment'))

    
    #@staticmethod
    #def update_ws_info():
    #    #retrieves WebServer info
    #    origin = Origin.instance()
    #    try:
    #        wso = WebServer.objects.get(pk=1)
    #    except WebServer.DoesNotExist:
    #        return
    #    result = wso.remote_action(view_name=u"check_info",
    #                              method   = GET,
    #                              apikey   = wso.apikey,
    #                              origin_id= origin.id)
    #    webservers = result.get('webservers', None)
    #    if not webservers:
    #        return
    #    for ws in webservers:
    #        up_to_date = ws.get('up_to_date', None)
    #        if not up_to_date:
    #            name        = ws.get('name'       , None)
    #            url         = ws.get('url'        , None)
    #            api_url     = ws.get('api_url'    , None)
    #            api_version = ws.get('api_version', None)
    #            apikey      = ws.get('apikey'     , None)
    #            
    #            #if all values are defined
    #            if all([name, url, api_url, api_version, apikey]):
    #                try:
    #                   wso = WebServer.objects.get(name=name)
    #                except WebServer.DoesNotExist:
    #                   wso = WebServer(name=name)
    #                data = {
    #                    'url' : url,
    #                    'api_url': api_url,
    #                    'api_version': api_version,
    #                    'apikey': apikey,
    #                }   
    #                wso.update(**data)
    #                wso.save()

    def is_online(self):
        """
        Checks if WebServer is online
        """
        hostname = self.url.replace('http://', '').rpartition(':')[0].rpartition('/')[0]
        answer = False
        for port in (443,80, 7000, 8000):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((hostname,port))
                answer = True
                break
            except:
                s.close()
                continue
        s.close()
        
        return answer
    
    
    def get_api(self, token=None, auth=None):
        _auth = auth if auth \
                else HTTPTokenAuth(token) if token \
                else HTTPTokenAuth(DEFAULT_TOKEN)
        return slumber.API(self.url, auth=_auth)
