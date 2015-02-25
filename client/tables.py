# -*- coding: utf-8 -*-

from django_tables2 import tables, columns
from django_tables2.utils import A

from .models import Backup
from .models.schedule import Schedule

import itertools

class BackupTable(tables.Table):
    row_number = columns.Column(empty_values=(), verbose_name='No.')
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

class ScheduleTable(tables.Table):
    row_number = columns.Column(empty_values=(), verbose_name='No.')
    edit = columns.LinkColumn('admin:client_schedule_change',
                                 args=[A('id')],
                                 orderable=False,
                                 verbose_name=u'Editar')
    
    def __init__(self, *args, **kwargs):
        super(ScheduleTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count()
        next(self.counter)
        
    def render_row_number(self):
        return '%d' % next(self.counter)
    
    #def render_edit(self):
    #    return 'Editar'
    
    class Meta:
        model = Schedule
        fields = ('row_number',
                  'destination',
                  'initial_time',
                  'rule',
                  'active',
                  'edit')
        order_by = ('initial_time')
    
