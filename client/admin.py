# -*- coding: utf-8 -*-

from django.core.exceptions import  PermissionDenied

from django.contrib import admin, messages
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
from .forms import OriginAddForm, OriginEditForm, ScheduleForm, NEW_USER, EXISTING_USER

class OriginAdmin(admin.ModelAdmin):
    form = OriginEditForm
    list_display = ('name', 'email', 'auth_token', 'remote_id')
    
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return MyAddForm
        else:
            return super(OriginAdmin, self).get_form(request, obj, **kwargs)

    def has_add_permission(self, request):
        return request.user.is_superuser and not Origin.objects.filter(pk=1).exists()

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def save_model(self, request, obj, form, change):
        super(OriginAdmin, self).save_model(request, obj, form, change)
        ws = WebServer.instance()
        
        if change:
            messages.add_message(request, messages.SUCCESS, u'Dados de %(name)s foram alterados no servidor %(server_name)s (%(server_url)s) com sucesso' % {
                'name': obj.name,
                'server_name': ws.name,
                'server_url': ws.url
            })
        else:
            ws = WebServer.instance()
            messages.add_message(request, messages.SUCCESS, u'%(new_or_existing)s %(name)s foi registrado no servidor %(server_name)s (%(server_url)s) com sucesso' % {
                'new_or_existing': u'Novo usuário' if form.cleaned_data['new_or_existing_user'] == NEW_USER else 'Usuário existente',
                'name': obj.name,
                'server_name': ws.name,
                'server_url': ws.url
        })    
        
    
    #def change_view(self, request,form_url=''):
    #    return HttpResponseForbidden()

class ScheduleAdmin(admin.ModelAdmin):
    form = ScheduleForm
    
    #def add_view(self, request, form_url='', extra_context=None):
    #    if request.method == GET:
    #        Destination.update(WebServer.instance(), Origin.objects.get(pk=1).remote_id)
    #    return super(ScheduleAdmin, self).add_view(request, form_url, extra_context)
    
    #def change_view(self, request,form_url=''):
    #    if request.method == GET:
    #        Destination.update(WebServer.instance(), Origin.objects.get(pk=1).remote_id)
    #    return super(ScheduleAdmin, self).change_view(request,form_url)

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
admin.site.register([Backup, RRule])
