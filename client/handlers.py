
from datetime import datetime
from cStringIO import StringIO
import gzip
import zlib
import os
import requests
import pytz
import dateutil.parser
import dateutil.tz

from django import forms
from django.core.management import call_command
from django.core.files.base import ContentFile
from django.utils import timezone
from client.conf.settings import settings, TBACKUP_DATETIME_FORMAT

from client.auth import HTTPTokenAuth
from client.models import Backup, Origin, WebServer, Schedule
from client import functions

class DataHandler(object):
    
    def __init__(self, origin=None, webserver=None):
        #current time
        self.run_time = functions.normalize_time(timezone.now())
        self.run_time_local = timezone.make_naive(self.run_time, pytz.timezone(settings.TIME_ZONE))
        now_str = datetime.strftime(self.run_time_local, TBACKUP_DATETIME_FORMAT)
        
        #get schedules to run now
        self.schedules = self.get_schedules_to_run()
        
        self.origin = origin
        self.webserver = webserver
        if isinstance(webserver, WebServer) and isinstance(origin, Origin):
            self.api = webserver.get_api(token=origin.auth_token)
        else:
            self.api = None
            
        self.filename = '%(username)s_%(datetime)s.gz' % {
            'username': self.origin.name,
            'datetime': now_str
        }
        
        
    def cache_dumpdata(self):
        self.contents = self.get_dumped_data()
    
    
    def get_schedules_to_run(self):
        """
        Fetches all active jobs scheduled to run now
        """
        #django converts UTC to localtime in filters, so we need to
        #use our run_time_local, a naive datetime object
        schedules = Schedule.objects.filter(active=True,
                                            initial_time__hour=self.run_time_local.hour,
                                            initial_time__minute=self.run_time_local.minute)
        return [s for s in schedules if s.is_runtime(self.run_time)]
    
    def get_dumped_data(self):
        '''
            Gets complete dump of the database in JSON format, Gzipped
        '''
        contents = StringIO()
        contents_gzipped = StringIO()
        
        #use natural keys to handle auto-generated
        #contenttypes and auth.permission properly
        call_command('dumpdata',
                     use_natural_keys=True,
                     exclude=['contenttypes', 'auth.permission'],
                     stdout=contents)
        contents.seek(0)
        
        gzip_file = gzip.GzipFile(fileobj=contents_gzipped, mode='w')
        gzip_file.write(contents.read())
        gzip_file.close()
        
        contents_gzipped.seek(0)
        return contents_gzipped

    def backup(self, schedule=None, destination=None):
        '''
            Backs up data
        '''
        
        if not self.api:
            raise Exception('origin and webserver instances must be passed to DataHandler''s constructor to connect to API')
        if not self.contents:
            raise Exception('dumpdata was not cached. Run cache_dumpdata')
        
        #create job
        if schedule:
            backup_obj = Backup(name=self.filename, schedule=schedule)
        else:
            backup_obj = Backup(name=self.filename)
            backup_obj.destination = destination
            
        backup_obj.full_clean()
        backup_obj.save()
        backup_obj.file.save(self.filename, ContentFile(self.contents))
        
        remote_backup_info = {
            'name': self.filename,
            'destination': backup_obj.destination,
            'date': self.run_time,
        }
        
        self.contents.seek(0)
        #post to server
        try:
            result = self.api.backups.post(remote_backup_info, files={'file': self.contents})
            if 'id' in result:
                backup_obj.remote_backup_date = self.run_time
                backup_obj.remote_id = result['id']
                backup_obj.save()
            else:
                raise Exception(_('Server response not recognized: %s' % result))
        except Exception as e:
            raise Exception(_('Error sending backup to server: %s' % e))
    
        return True
    
    def restore(self, remote_backup_id):
        '''
            Restores data into project, overriding current data
        '''
        tmp_file = '/tmp/loaddata_fixture.json'
        auth = HTTPTokenAuth(self.origin.auth_token)
        
        #mounts download url to use with requests lib to download as stream
        url = '%(host)s/backups/%(id)s/?fileformat=raw'% {
            'host': self.webserver.url,
            'id': remote_backup_id
        }
        
        #get metadata for the restored backup
        self.restored_bkp_metadata = self.api.backups(remote_backup_id).get()
        
        #use zlib with magic number to handle gzip chunks
        z = zlib.decompressobj(16+zlib.MAX_WBITS)
        #use requests instead of slumber API to handle chunk (stream) downloads
        with open(tmp_file, 'wb') as f:
            response = requests.get(url, auth=auth, stream=True)
            if not response.ok:
                raise forms.ValidationError(u'Erro inesperado: %s' % response)
            for chunk in response.iter_content(1024):
                if chunk:
                    f.write(z.decompress(chunk))
                    
        out=StringIO()
        err=StringIO()
        #FLUSH ALL DB AND THEN LOAD DOWNLOADED FIXTURE
        call_command('flush', interactive=False)
        call_command('loaddata', tmp_file, stdout=out, stderr=err)
        
        #if error
        err.seek(0, os.SEEK_END)
        if err.tell() > 0:
            err.seek(0)
            raise Exception(err.read())
        
        #deletes tmp_file
        os.remove(tmp_file)
        
        self.sync_backup_info()
        return out.read()
    
    def sync_backup_info(self):
        
        #get info from restored metadata obtained in restore method
        if 'id' in self.restored_bkp_metadata:
            remote_backups = self.api.backups.get(min_date=self.restored_bkp_metadata['date'])
            remote_backups = sorted(remote_backups, key=lambda k: k['date'])
            
            for r_b in remote_backups:
                #parses datetime in isoformat string to datetime object
                dt = dateutil.parser.parse(r_b['date'])
                #converts UTC datetime to local datetime
                local_dt = timezone.make_naive(dt, pytz.timezone(settings.TIME_ZONE))
                
                schedule = Schedule.objects \
                                   .filter(active=True,
                                           initial_time__hour=local_dt.hour,
                                           initial_time__minute=local_dt.minute) \
                                   .first()
                if schedule:
                    b = Backup(schedule=schedule)
                else:
                    b = Backup()
                    
                b.remote_backup_date = r_b['date']
                b.destination = r_b['destination']
                b.remote_id = r_b['id']
                b.name = r_b['name']
                b.save()
        
    def fix_contenttypes_mismatch(self):
        '''
            if contenttype id does not match models properly, run this method.
            What this method does is:
            - dumpdata natural without contenttypes and auth.permission
              (that way, every relation from groups or users to
               auth.permission and every relation to contenttypes
               will be preserved after syncing new db)
            - flush
            - loaddata of the dumped data
            - rm fixture
        '''
        tmp_file = '/tmp/fix_contenttypes_mismatch.json'
        with open(tmp_file, 'wb') as f:
            call_command('dumpdata',
                         use_natural_keys=True,
                         exclude=['contenttypes','auth.permission'],
                         stdout=f)
        call_command('flush', interactive=False)
        call_command('loaddata', tmp_file)
        os.remove(tmp_file)
    
    