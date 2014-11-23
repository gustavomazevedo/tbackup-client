from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import FormView
from django.shortcuts import render
from django.template.context import RequestContext
from .models import Backup, OpLog
from .models.location import Destination, Origin, WebServer
from .models.schedule import RRule, Schedule

from django_tables2 import RequestConfig

from .tables import BackupTable, DestinationTable, OpLogTable, OriginTable, RRuleTable, ScheduleTable, WebServerTable

from .forms import ConfirmRestoreForm

# Create your views here.

def render_table(request, table_class):
    table_class._meta.attrs = {'class': 'paleblue'}
    table = table_class(table_class._meta.model.objects.all())
    RequestConfig(request).configure(table)
    return render(request, 'table.html', {'table': table})

def backups(request):
    return render(request, 'backups.html', {'backups': Backup.objects.all()})

def oplogs(request):
    return render(request, 'backups.html', {'backups': Backup.objects.all()})

def destinations(request):
    return render_table(request, DestinationTable)

def origins(request):
    return render_table(request, OriginTable)

def rrules(request):
    return render_table(request, RRuleTable)

def schedules(request):
    return render_table(request, ScheduleTable)

def webservers(request):
    return render_table(request, WebServerTable)

#@staff_member_required
class ConfirmRestoreView(FormView):
    form_class = ConfirmRestoreForm
    
    
    #@staff_member_required    
    #def get(request, pk=None):
    #    form = 
    
    #@staff_member_required
    #def post(request, pk=None):
    #    pass