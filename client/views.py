# -*- coding: utf-8 -*-

from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import FormView
from django.shortcuts import render, get_object_or_404
from .models import Backup
from .models.location import Origin, WebServer

from django_tables2 import RequestConfig

from .handlers import DataHandler
from .tables import BackupTable, ScheduleTable
from .forms import ConfirmRestoreForm

from django.contrib import messages
from django.shortcuts import redirect

# Create your views here.

def render_table(request, table_class):
    table_class._meta.attrs = {'class': 'paleblue'}
    model = table_class._meta.model
    table = table_class(model.objects.all())
    pagename = model._meta.verbose_name_plural.capitalize()
    RequestConfig(request).configure(table)
    return render(request, 'table.html', {'table': table, 'pagename': pagename})

@staff_member_required
def backups(request):
    return render_table(request, BackupTable)

def schedules(request):
    return render_table(request, ScheduleTable)

def schedule_change(request, id):
    return redirect('admin:client_schedule_change', id)
    
class ConfirmRestoreView(FormView):
    template_name = 'restore_confirmation.html'
    form_class = ConfirmRestoreForm
    success_url = '/client/backups/'
    
    @method_decorator(staff_member_required)
    def get(self, request, pk=None):
        self.backup = get_object_or_404(Backup, pk=pk)
        form = ConfirmRestoreForm()
        return self.render_to_response(self.get_context_data(form=form))
    
    @method_decorator(staff_member_required)
    def post(self, request, pk=None):
        self.backup = get_object_or_404(Backup, pk=pk)
        form = ConfirmRestoreForm(request.POST)
        if form.is_valid():
            result = self.form_valid(form)
            messages.add_message(request, messages.SUCCESS, u'Dados restaurados com sucesso')
        else:
            result = self.form_invalid(form)
            messages.add_message(request, messages.ERROR, u'Erro na restauração de dados. Favor Contactar os administratores.')
        
        return result

    def get_context_data(self, **kwargs):
        data = super(ConfirmRestoreView, self).get_context_data(**kwargs)
        data['object'] = self.backup
        return data
    
    def form_valid(self, form):
        
        handler = DataHandler(origin=Origin.instance(),webserver=WebServer.instance())
        
        #before restoring, run a backup without schedule
        handler.cache_dumpdata()
        #same destination as the restored one
        ok = handler.backup(destination=self.backup.destination)
        
        if ok:
            #id to restore
            handler.restore(self.backup.remote_id)
            
        
        return super(ConfirmRestoreView, self).form_valid(form)
    