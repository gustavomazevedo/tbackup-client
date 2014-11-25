# -*- coding: utf-8 -*-

from django.core.exceptions import  PermissionDenied

from django.contrib import admin
from django.http import HttpResponseForbidden
# Register your models here.

from .conf.settings import GET

from .models import (
    Destination,
    Origin,
    WebServer,
    Backup,
  # Plan
   Schedule,
   RRule
   #Log,
  # BackupStatus,
  )
#from .forms import ConfigForm, OriginForm
from .forms import OriginForm

class OriginAdmin(admin.ModelAdmin):
    form = OriginForm
    
    def has_add_permission(self, request):
        return request.user.is_superuser and not Origin.objects.filter(pk=1).exists()

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    #def save_model(self, request, obj, form, change):
    #    data = WebServer.instance().register(request.POST.get('name', None))
    #    if not data:
    #        raise PermissionDenied()
    #    ws = WebServer.instance()
    #    ws.apikey = data.get('apikey')
    #    ws.save()
    #    obj.remote_id = data.get('id')
    #    obj.save()
    
    #def change_view(self, request,form_url=''):
    #    return HttpResponseForbidden()

class ScheduleAdmin(admin.ModelAdmin):
    
    #def has_add_permission(self, request):
    #    return Origin.objects.filter(pk=1).exists()

    #def has_delete_permission(self, request, obj=None):
    #    return self.origin_exists
    
    #def has_change_permission(self, request, obj=None):
    #    return self.origin_exists

    def add_view(self, request, form_url='', extra_context=None):
        if request.method == GET:
            Destination.update(WebServer.instance(), Origin.objects.get(pk=1).remote_id)
        return super(ScheduleAdmin, self).add_view(request, form_url, extra_context)
    
    def change_view(self, request,form_url=''):
        if request.method == GET:
            Destination.update(WebServer.instance(), Origin.objects.get(pk=1).remote_id)
        return super(ScheduleAdmin, self).change_view(request,form_url)

class WebServerAdmin(admin.ModelAdmin):
    #readonly_fields = ('apikey',)
    list_display = ( 'name',
    #                 'apikey',
                     'url'
                   )
    def has_add_permission(self, request):
        return not WebServer.objects.filter(pk=1).exists()

    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return WebServer.objects.filter(pk=1).exists()
    
admin.site.register(Origin, OriginAdmin)
if Origin.objects.filter(pk=1).exists():
    admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(WebServer, WebServerAdmin)
admin.site.register([Destination, Backup, RRule])
