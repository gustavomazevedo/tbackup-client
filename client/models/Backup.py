# -*- coding: utf-8 -*-

from hashlib      import sha1 as SHA
from django.db    import models
from datetime     import datetime
from django.utils import timezone

from django.core.urlresolvers import reverse
from client.conf.settings import TBACKUP_DATETIME_FORMAT, settings
from django.utils.html import format_html
from django.core.files.base import ContentFile
            
            
from client import functions

from client.models.location import Origin, WebServer

import os.path

def get_path_name(instance, filename):
    return os.path.join('.', instance.destination, filename)

class Backup(models.Model):
    #enum for states
    #PENDIND = None
    #FAILURE = False
    #SUCCESS = True
    #IDLE          = 'IDLE'
    #RUNNING       = 'RUNNING'
    #ERROR_RUNNING = 'ERROR_RUNNING'
    #WAITING       = 'WAITING'
    #SENDING       = 'SENDING'
    #ERROR_SENDING = 'ERROR_SENDING'
    #FINISHED      = 'FINISHED'
    #REMOVED_LOCAL = 'REMOVED_LOCAL'
    ##choices for state column
    #STATE_CHOICES = (
    #    (IDLE         , u'Não Iniciado.'),
    #    (RUNNING      , u'Executando backup local.'),
    #    (ERROR_RUNNING, u'Erro ao tentar executar o backup local.'),
    #    (WAITING      , u'Aguardando para enviar.'),
    #    (SENDING      , u'Enviando para servidor.'),
    #    (ERROR_SENDING, u'Erro ao tentar enviar para servidor.'),
    #    (FINISHED     , u'Backup finalizado.'),
    #    (REMOVED_LOCAL, u'Cópia local removida. Restauro apenas online.'),
    #)
    ##enum for kind
    #SCHEDULED     = 'SCHEDULED'
    #EXTRAORDINARY = 'EXTRAORDINARY'
    ##choices for kind column
    #KIND_CHOICES = (
    #    (SCHEDULED    , 'Agendado'),
    #    (EXTRAORDINARY, 'Especial'),
    #)
    
    TIMEFORMAT = '%Y%m%d%H%M'
    
    #model fields
    name = models.CharField(max_length=256, verbose_name=u'nome')
    file = models.FileField(upload_to=get_path_name, null=True, blank=True, verbose_name=u'arquivo')
    
    schedule    = models.ForeignKey('Schedule', null=True, blank=True, verbose_name=u'agendamento')
    origin      = models.CharField(max_length=256, null=True, blank=True, verbose_name=u'cliente')
    destination = models.CharField(max_length=256, null=True, blank=True, verbose_name=u'destino')
    
    #local_backup_date  = models.DateTimeField(null=True)
    remote_backup_date = models.DateTimeField(null=True, blank=True, verbose_name=u'data do backup remoto')
    
    last_error = models.TextField(null=True, blank=True)
    remote_id  = models.BigIntegerField(null=True, blank=True, verbose_name=u'id remoto')
    
    #time     = models.DateTimeField()
    
    #size        = models.BigIntegerField(null=True)
    
    #kind = models.CharField(max_length=13,
    #                        choices=KIND_CHOICES,
    #                        default=SCHEDULED)
    #state = models.CharField(max_length=13,
    #                         choices=STATE_CHOICES,
    #                         default=IDLE)
    
    
    @property
    def local_completed(self):
        return self.file is not None
    
    @property
    def remote_completed(self):
        return self.remote_backup_date is not None
    
    @property
    def restore(self):
        return 'Restaurar'
    
    #meta config
    class Meta:
        #app_label required when scathering models in multiple files
        app_label = 'client'
        
    def __unicode__(self):
        return self.name
    
    #def save(self, *args, **kwargs):
    #    self.full_clean()
    #    super(Backup, self).save(*args, **kwargs)
    
    def clean(self):
        super(Backup, self).clean()
        
        #logs current origin name from Origin
        self.origin = Origin.instance().name
        #logs current destination name from Schedule:
        if self.schedule:
            self.destination = self.schedule.destination
        #backs up data
        #if self.file is None:
        #    self.file = self.dumpdata_apps()
    
    def remote_url(self):
        from django.core.urlresolvers import reverse
        from client import views
        return functions.to_hyperlink(reverse(views.restore) + self.remote_id)
    remote_url.allow_tags = True
    remote_url.short_description = ''
    
    def get_name(self):
        return u'%(origin_name)s_%(dt)s_%(kind)s' % {
            'origin_name': Origin.instance().name,
            'dt'         : time.strftime(self.TIMEFORMAT, self.time),
            'kind'       : self.kind,
        }
    
    def restore_link(self):
        if self.state in (self.FINISHED, self.REMOVED_LOCAL):
            return format_html('<a href="{0}">Restore<img src="{1}"/></a>',
                               reverse('url_restore', args=(self.id,)),
                               '%simg/Refresh.png' % settings.STATIC_URL)
        return ''
    restore_link.short_description = 'Restaurar'
    restore_link.allow_tags = True
    
    
    
    #def advance_state(self):
    #    print 'from %s ' % self.state
    #    if self.state == self.IDLE:
    #        self.state = self.RUNNING
    #    elif self.state == self.RUNNING:
    #        self.state = self.WAITING
    #    elif self.state == self.WAITING:
    #        self.state = self.SENDING
    #    elif self.state == self.SENDING:
    #        self.state = self.FINISHED
    #    elif self.state == self.FINISHED:
    #        self.state = self.REMOVED_LOCAL
    #    else:
    #        #raise Exception('State: %s. Cannot advance state.' % self.state)
    #        return
    #    print 'to %s ' % self.state
            
    def update_error(self, exc_info):
        exc_type, exc_value, exc_traceback = exc_info
        self.last_error = \
            """
               %(type)s: %(value)s
               ==============
               %(traceback)s
            """ % {
                    'type'     : exc_type,
                    'value'    : exc_value,
                    'traceback': exc_traceback,
                  }

        