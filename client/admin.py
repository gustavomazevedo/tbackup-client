# -*- coding: utf-8 -*-

import urllib2

from django.contrib import admin
from django.http import HttpResponse, HttpResponseForbidden
# Register your models here.

from .models import (
    Destination
  , Origin
  , WebServer
  #, Plan
  , Config
  , Log
  , BackupStatus
  )
from .forms import ConfigForm

class OriginAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not Origin.objects.filter(pk=1).exists()

    def has_delete_permission(self, request, obj=None):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True

    def add_view(self, request, form_url='', extra_context=None):
        if request.method == 'POST':
            name = request.POST.get('name', None)
            data = Origin.register(name)
            if not data:
                return HttpResponse(u'<h1>Erro</h1><br><h2>Não foi possível registrar esta estação no servidor</h2>')
            result = super(OriginAdmin, self).add_view(request, form_url, extra_context)
            
            apikey = data.get(u"apikey", None)
            if apikey:
                ws = WebServer.get()    
                ws.apikey = apikey
                ws.save()
            origin_id = data.get(u"id", None)
            if origin_id:
                origin = Origin.objects.get(name=name)
                origin.remote_id = origin_id
                origin.save()
            return result 
        return super(OriginAdmin, self).add_view(request, form_url, extra_context)
    def change_view(self, request,form_url=''):
        return HttpResponseForbidden()

class ConfigAdmin(admin.ModelAdmin):
    form = ConfigForm

    def has_add_permission(self, request):
        return Origin.objects.filter(pk=1).exists()

    def has_delete_permission(self, request, obj=None):
        return Origin.objects.filter(pk=1).exists()
    
    def has_change_permission(self, request, obj=None):
        return Origin.objects.filter(pk=1).exists()

    def add_view(self, request, form_url='', extra_context=None):
        if request.method =='GET':
            Destination.update()
        return super(ConfigAdmin, self).add_view(request, form_url, extra_context)
    
    def change_view(self, request,form_url=''):
        if request.method =='GET':
            Destination.update()
        return super(ConfigAdmin, self).change_view(request,form_url)

class WebServerAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not WebServer.objects.filter(pk=1).exists()

    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return WebServer.objects.filter(pk=1).exists()
    
admin.site.register(Destination)
admin.site.register(Origin, OriginAdmin)
#admin.site.register(Configuration)
admin.site.register(WebServer, WebServerAdmin)
#admin.site.register(Plan)
admin.site.register(Config, ConfigAdmin)
admin.site.register(Log)
#admin.site.register(BackupStatus)
