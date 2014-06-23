# -*- coding: utf-8 -*-

import urllib2

from django.core.exceptions import  PermissionDenied

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
from .forms import ConfigForm, OriginForm

class OriginAdmin(admin.ModelAdmin):
    form = OriginForm
    
    def has_add_permission(self, request):
        return not Origin.objects.filter(pk=1).exists()

    def has_delete_permission(self, request, obj=None):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        data = WebServer.get().register(request.POST.get('name', None))
        if not data:
            raise PermissionDenied()
        ws = WebServer.get()
        ws.apikey = data.get('apikey')
        ws.save()
        obj.remote_id = data.get('id')
        obj.save()
    
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
            Destination.update(Origin.objects.get(pk=1).remote_id)
        return super(ConfigAdmin, self).add_view(request, form_url, extra_context)
    
    def change_view(self, request,form_url=''):
        if request.method =='GET':
            Destination.update(Origin.objects.get(pk=1).remote_id)
        return super(ConfigAdmin, self).change_view(request,form_url)

class WebServerAdmin(admin.ModelAdmin):
    readonly_fields = ('apikey',)
    list_display = ( 'name'
                   , 'apikey'
                   , 'url'
                   )
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
