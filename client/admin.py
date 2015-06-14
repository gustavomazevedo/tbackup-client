# -*- coding: utf-8 -*-

from django.contrib import admin, messages

from .models import Origin, WebServer, Schedule
from .forms import OriginAddForm, OriginEditForm, ScheduleForm, NEW_USER, EXISTING_USER

class OriginAdmin(admin.ModelAdmin):
    #form = OriginEditForm
    list_display = ('name', 'email', 'auth_token', 'remote_id')
    
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            self.form = OriginAddForm
        else:
            self.form = OriginEditForm
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
            messages.add_message(request, messages.SUCCESS, u'%(new_or_existing)s %(name)s foi %(action)s servidor %(server_name)s (%(server_url)s) com sucesso' % {
                'new_or_existing': u'Novo usuário' if form.cleaned_data['new_or_existing_user'] == NEW_USER else u'Usuário existente',
                'action': u'registrado no' if form.cleaned_data['new_or_existing_user'] == NEW_USER else u'recuperado do',
                'name': obj.name,
                'server_name': ws.name,
                'server_url': ws.url
        })    
        
    
    #def change_view(self, request,form_url=''):
    #    return HttpResponseForbidden()

class ScheduleAdmin(admin.ModelAdmin):
    form = ScheduleForm

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
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(WebServer, WebServerAdmin)

