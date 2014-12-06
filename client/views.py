from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.views.generic import FormView
from django.shortcuts import render, get_object_or_404
from django.template.context import RequestContext
from .models import Backup, OpLog
from .models.location import Destination, Origin, WebServer
from .models.schedule import RRule, Schedule

from django_tables2 import RequestConfig

from .handlers import DataHandler
from .tables import BackupTable, DestinationTable, ScheduleTable
from .forms import ConfirmRestoreForm

# Create your views here.

def render_table(request, table_class):
    table_class._meta.attrs = {'class': 'paleblue'}
    table = table_class(table_class._meta.model.objects.all())
    RequestConfig(request).configure(table)
    return render(request, 'table.html', {'table': table})

@staff_member_required
def backups(request):
    return render_table(request, BackupTable)

def destinations(request):
    return render_table(request, DestinationTable)

def origins(request):
    return render_table(request, OriginTable)

#@staff_member_required
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
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

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
    