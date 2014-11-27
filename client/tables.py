from django_tables2 import tables

from .models import Backup, OpLog
from .models.location import Destination, Origin, WebServer
from .models.schedule import RRule, Schedule

class BackupTable(tables.Table):
    class Meta:
        model = Backup
    
class OpLogTable(tables.Table):
    class Meta:
        model = OpLog

class DestinationTable(tables.Table):
    class Meta:
        model = Destination
        
class OriginTable(tables.Table):
    class Meta:
        model = Origin

class WebServerTable(tables.Table):
    class Meta:
        model = WebServer

class RRuleTable(tables.Table):
    class Meta:
        model = RRule

class ScheduleTable(tables.Table):
    class Meta:
        model = Schedule
    
    
