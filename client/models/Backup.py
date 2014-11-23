# -*- coding: utf-8 -*-

from hashlib      import sha1 as SHA
from django.db    import models
from datetime     import datetime
from django.utils import timezone

from django.core.urlresolvers import reverse
from client.conf.settings import DATETIME_FORMAT, settings

from client import functions

def get_path_name(instance, filename):
    return u'/'.join([instance.schedule.destination.name, filename])

class Backup(models.Model):
    #enum for states
    IDLE          = 'IDLE'
    RUNNING       = 'RUNNING'
    ERROR_RUNNING = 'ERROR_RUNNING'
    WAITING       = 'WAITING'
    SENDING       = 'SENDING'
    ERROR_SENDING = 'ERROR_SENDING'
    FINISHED      = 'FINISHED'
    REMOVED_LOCAL = 'REMOVED_LOCAL'
    #choices for state column
    STATE_CHOICES = (
        (IDLE         , u'Não Iniciado.'),
        (RUNNING      , u'Executando backup local.'),
        (ERROR_RUNNING, u'Erro ao tentar executar o backup local.'),
        (WAITING      , u'Aguardando para enviar.'),
        (SENDING      , u'Enviando para servidor.'),
        (ERROR_SENDING, u'Erro ao tentar enviar para servidor.'),
        (FINISHED     , u'Backup finalizado.'),
        (REMOVED_LOCAL, u'Cópia local removida. Restauro apenas online.'),
    )
    #enum for kind
    SCHEDULED     = 'SCHEDULED'
    EXTRAORDINARY = 'EXTRAORDINARY'
    #choices for kind column
    KIND_CHOICES = (
        (SCHEDULED    , 'Agendado'),
        (EXTRAORDINARY, 'Especial'),
    )
    
    TIMEFORMAT = '%Y%m%d%H%M'
    
    #model fields
    name      = models.CharField(max_length=256)
    schedule  = models.ForeignKey('Schedule')
    time      = models.DateTimeField()
    local_file= models.FileField(upload_to=get_path_name,
                                 null=True)
    size      = models.BigIntegerField(null=True)
    destination_name = models.CharField(max_length=256, null=True)
    kind = models.CharField(max_length=13,
                            choices=KIND_CHOICES,
                            default=SCHEDULED)
    state = models.CharField(max_length=13,
                             choices=STATE_CHOICES,
                             default=IDLE)
    last_error = models.TextField(null=True)
    remote_id  = models.BigIntegerField()
    
    #meta config
    class Meta:
        #app_label required when scathering models in multiple files
        app_label = 'client'
        
    def __unicode__(self):
        return self.name
    
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
            return '<a href="%(restore)s">Restore<img src="%(image)s"/></a>' % {
                'restore': reverse('url_restore', args=(self.id,)),
                'image'  : '%simg/Refresh.png' % settings.STATIC_URL, 
            }
        return ''
    restore_link.short_description = 'Restaurar'
    restore_link.allow_tags = True
    
    def advance_state(self):
        print 'from %s ' % self.state
        if self.state == self.IDLE:
            self.state = self.RUNNING
        elif self.state == self.RUNNING:
            self.state = self.WAITING
        elif self.state == self.WAITING:
            self.state = self.SENDING
        elif self.state == self.SENDING:
            self.state = self.FINISHED
        elif self.state == self.FINISHED:
            self.state = self.REMOVED_LOCAL
        else:
            #raise Exception('State: %s. Cannot advance state.' % self.state)
            return
        print 'to %s ' % self.state
            
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
    
    def backup(self):
        print {
            'function': 'BACKUP',
            'dest': self.destination_name,
            'pk': self.pk,
            'time': self.time,
            'state': self.state,
            'schedule': self.schedule,
            'error': self.last_error,
        }
        if self.ERROR_RUNNING:
            self.state = self.IDLE
        if self.state != self.IDLE:
            #raise Exception('State: %s. Cannot run local backup.' % self.state)
            return
        self.advance_state()
        try:
            self.local_backup()
            self.advance_state()
        except:
            import sys
            self.update_error(sys.exc_info())
            self.state = self.ERROR_RUNNING
        
        #schedule next backup if there's a recurrence rule    
        next_run = self.schedule.next_run()
        if next_run is not None:
            Backup.objects.create(schedule=self.schedule,
                                  time=next_run)
        self.save()
        
        
    def send(self, web_server):
        print {
            'function': 'SEND',
            'dest': self.destination_name,
            'pk': self.pk,
            'time': self.time,
            'state': self.state,
            'schedule': self.schedule,
            'error': self.last_error,
        }
        if self.ERROR_SENDING:
            self.state = self.WAITING
        if self.state != self.WAITING:
            #raise Exception('State: %s. Cannot send backup' % self.state)
            return
            
        self.advance_state()
        try:
            self.remote_backup()
            self.advance_state()
        except:
            import sys
            self.update_error(sys.exc_info())
            self.state = self.ERROR_SENDING
        
        self.save()    
        return None

    def local_backup(self):
        dt = timezone.now()
        dt_str = datetime.strftime(dt, DATETIME_FORMAT)
        date = dt_str[:dt_str.rfind('.')]
        
        origin = Origin.objects.get(pk=1)
        filename = origin.name + '_' + self.date
        
        app_filters = {
            'django': self.schedule.backup_system,
            'client': self.schedule.backup_tbackup_config
        }
        
        installed_apps = settings.INSTALLED_APPS
        appsgen = (a for a in installed_apps)
        for packname, will_backup in app_filters:
            if not will_backup:
                appsgen = (a for a in appsgen if not a.startswith(packname))
        apps = list(appsgen)
        
        #apps = [a for a in installed_apps
        #        if (not (a.startswith('django') or a.startswith('tbackup')))]
        
        
        #print 'client: apps'
        #print apps       
        #print 'FILENAME'
        #print filename
        
        f = open(os.path.join(TBACKUP_DUMP_DIR,filename), "wb")
        call_command('dumpdata', *apps, stdout=f)
        f.close()
                
        newfilename = filename + '.db.gz'
        
        f_in  = open(os.path.join(TBACKUP_DUMP_DIR,filename), 'rb')
        f_out = gzip.open(os.path.join(TBACKUP_DUMP_DIR,newfilename), 'wb',9)
        
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()
        os.remove(os.path.join(TBACKUP_DUMP_DIR,filename))
        
        log.filename = newfilename
        log.local_status = True

    
    def remote_backup(self, log):
        #from base64 import b64encode
        sha1 = SHA.new()

        
        ws = WebServer.objects.get(pk=1)
        #url = ws.url + 'tbackup_server/backup/'
        #print url
        #url = self._resolve_url('/a/creative/uploadcreative')
        #url = 'http://127.0.0.1:8080/server/backup/'
        f = open(os.path.join(TBACKUP_DUMP_DIR,log.filename), 'rb')
        sha1.update(f.read())
        f.seek(0)
        files = {'file': (log.filename,f)}
        #data = {'destination': log.destination.name,
        #        'sha1sum' : sha1.hexdigest(),
        #        'date' : str(log.date),
        #        'origin_name' : Origin.objects.get(pk=1).name}
        #req_msg = {'error' : 'false', 
        #           'encrypted' : 'false', 
        #           'key' : 'false',
        #           'value' : json.dumps(data)}
        response = requests.post(url, files=files, data=req_msg, verify=False)
        
        #print 'client:'
        #print response.status_code
        
        if response.status_code != 200:
            print 'response error'
            print response.status_code
            log.remote_status = False
            return
        
        response_text = json.loads(response.text)
        print response_text

        log.remote_status = True
        
        return None
