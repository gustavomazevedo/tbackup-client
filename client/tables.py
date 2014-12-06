# -*- coding: utf-8 -*-

from django_tables2 import tables, columns
from django_tables2.utils import A

from .models import Backup
from .models.location import Destination, Origin
from .models.schedule import Schedule

import itertools

class BackupTable(tables.Table):
    row_number = columns.Column(empty_values=(), verbose_name='#')
    schedule = columns.Column(empty_values=())
    restore = columns.LinkColumn('client:restore',
                                 args=[A('pk')],
                                 orderable=False,
                                 verbose_name=u'Restaurar')
    
    def __init__(self, *args, **kwargs):
        super(BackupTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count()
        next(self.counter)
    
    def render_row_number(self):
        return '%d' % next(self.counter)
    
    def render_schedule(self, value):
        if value:
            return value
        else:
            return u'antes da restauração'
    
    class Meta:
        model = Backup
        fields = ('row_number',
                  'name',
                  'schedule',
                  'remote_backup_date',
                  'restore')
        order_by = ('-remote_backup_date')

class DestinationTable(tables.Table):
    class Meta:
        model = Destination
        
class OriginTable(tables.Table):
    class Meta:
        model = Origin

class ScheduleTable(tables.Table):
    class Meta:
        model = Schedule
    
    
