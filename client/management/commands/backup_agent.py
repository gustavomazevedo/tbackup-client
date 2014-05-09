# -*- coding: utf-8 -*-

import os
import gzip
#from cStringIO import StringIO
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, make_option
from django.utils import simplejson as json

from tbackup_client.models import (Origin,
                                   WebServer, 
                                   Log, 
                                   Config, 
                                   Destination, 
                                   BackupStatus)


PROJECT_DIR = os.path.normpath(os.path.join(
                    os.path.dirname(os.path.realpath(__file__)), '../../../'))
DUMP_DIR = os.path.normpath(os.path.join(PROJECT_DIR, 'tbackup_client/dumps/'))

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--check-backups', '-e',
            action='store_true',
            dest='check_backups',
            help='Checks up backup jobs and runs them if interval is reached'),
        #make_option('--update-config', '-u',
        #    dest='update_config',
        #    default=False,
        #    help='Updates configuration file'),
        #make_option('--delete-old-backups', '-d',
        #    dest='delete_old_backups',
        #    default=False,
        #    help='Deletes local backups older than 14 days'),
        make_option('--fill-data', '-f',
            action='store_true',
            dest='fill_data',
            help='fills_data'),
        make_option('--check-not-sent', '-c',
            action='store_true',
            dest='check_not_sent',
            help='Sends pending local backups to remote server')
        )
    
    def handle(self, *args, **options):
        #print "testando handle"
        #print options
        #Don't accept commands if origin is not registered
        try:
            Origin.objects.get(pk=1)
        except Origin.DoesNotExist:
            return
        
        backupHandler = BackupHandler()
        #print options
        if options.get('check_backups', False):
            #print 'entrei em check_backups'
            backupHandler.check_backups()
#        elif options['update_config']:
#            backupHandler.update_config()
#        elif options['delete_old_backups']:
#            backupHandler.delete_old_backups()
        elif options.get('fill_data', False):
            fill_data()
        elif options.get('check_not_sent', False):
            backupHandler.check_not_sent()
        
def fill_data():
    from dummy_app.models import DummyData
    for i in xrange(5):
        DummyData.objects.create(
                                 name='name %i' %i,
                                 type='type %i' %i
                                )
    
class BackupHandler():

#    def delete_old_backups(self):
#        fourteen_days_ago = datetime.now() - datetime.timedelta(days=14)
#        backuphistory = Log.objects.filter(
#            local_status=True,
#            remote_status=True,
#            dump_date__lt=fourteen_days_ago)
#        
#        for backup in backuphistory:
#            os.remove(os.path.join(DUMP_DIR, backup.filename))
#            backup.local_status = False
#            backup.save()

#    def update_config(self):
#        try:
#            server = WebServer.objects.get(pk=1)
#        except WebServer.DoesNotExist:
#            server = bkpagent.setup_server()
#            
#        cmd = ('rsync -e "ssh -p {0} -l {1}" -avz --delete-excluded {2} {3}'
#               .format(server.port, server.user, server.configpath, CONFIG_DIR))
#            
#        stdout, stderr = self.process(cmd)
#        self.command_log(stdout, stderr)
    
    def check_not_sent(self):
        not_sent = Log.objects.filter(
            local_status=True,
            remote_status=False)
        for log in not_sent:
            self.remote_backup(log)
            log.save()
        
    def check_backups(self): 
        status = BackupStatus.objects.get_or_create(pk=1)[0]
        #print status.executing
        if status.executing:
            status.save()
            return
        #print status.executing
        status.executing = True

        try:
            status.save()
        except:
            return
        
        now = datetime.now()
        now -= timedelta(microseconds=now.microsecond)
        configs = Config.objects.all()
        #print configs
        for config in configs:
            delta = now - config.last_backup
            #print now
            #print config.last_backup
            #print delta
            #print delta.seconds
            if (delta.seconds + 86400 * delta.days) >= config.interval:
                try:
                    config.last_backup = now
                    destination = Destination.objects.get(name=config.destination.name)
                    log = Log.objects.create(
                                              destination=destination,
                                              date=now)
                    self.local_backup(config, log)
                    log.save()
                    config.save()
                    self.remote_backup(log)
                    log.save()
                    config.save()
                except Exception:
                    import traceback
                    traceback.print_exc()
                    status.executing = False
                    status.save()
        
        status.executing = False
        status.save()
        
    def local_backup(self, config, log):
        dt = str(config.last_backup).replace(' ','_').replace(':','-')
        self.date = dt[:dt.rfind('.')]
        
        origin = Origin.objects.get(pk=1)
        filename = origin.name + '_' + self.date
        
        installed_apps = settings.INSTALLED_APPS
        apps = [a for a in installed_apps if (not (a.startswith('django') or a.startswith('tbackup')))]
        
        #print 'client: apps'
        #print apps       
        #print 'FILENAME'
        #print filename
        
        f = open(os.path.join(DUMP_DIR,filename),"wb")
        call_command('dumpdata', *apps, stdout=f)
        f.close()
                
        newfilename = filename + '.db.gz'
        
        f_in  = open(os.path.join(DUMP_DIR,filename), 'rb')
        f_out = gzip.open(os.path.join(DUMP_DIR,newfilename),'wb',9)
        
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()
        os.remove(os.path.join(DUMP_DIR,filename))
        
        log.filename = newfilename
        log.local_status = True

    
    def remote_backup(self, log):

        #from base64 import b64encode
        from Crypto.Hash import SHA
        sha1 = SHA.new()
        #with open(os.path.join(DUMP_DIR,log.filename), 'rb') as f:
        #    raw_data = str()
        #    encoded_string = str()
        #    #9KB(9216) block:
        #    #- multiple of 16 (2bytes) for sha1 to work in chunks
        #    #- multiple of 24 (3bytes) for b64encode to work in chunks 
        #    #- near 8KB for optimal sha1 speed
        #    for data in iter(lambda: f.read(9216), b''):
        #        raw_data += data
        #        encoded_string += b64encode(data)
        #        sha1.update(data)
        #    sha1sum = sha1.hexdigest()
        #     
        #value = {
        #           'destination' : 'Gruyere - LPS',
        #           'file' : encoded_string,
        #           'filename' : log.filename,
        #           #'sha1sum': self.get_sha1sum(raw_data),
        #           'sha1sum': sha1sum,
        #           #'origin_pubkey' : origin_pubkey
        #           'origin_name' : Origin.objects.get(pk=1).name,
        #          }
        #request_message = {
        #                   'error' : False,
        #                   'encrypted' : False,
        #                   'key': False,
        #                   'value' : value
        #                 }
        import requests
        
        ws = WebServer.objects.get(pk=1)
        url = ws.url + 'tbackup_server/backup/'
        print url
        #url = self._resolve_url('/a/creative/uploadcreative')
        #url = 'http://127.0.0.1:8080/server/backup/'
        f = open(os.path.join(DUMP_DIR,log.filename), 'rb')
        sha1.update(f.read())
        f.seek(0)
        files = {'file': (log.filename,f)}
        data = {'destination': log.destination.name,
                'sha1sum' : sha1.hexdigest(),
                'date' : str(log.date),
                'origin_name' : Origin.objects.get(pk=1).name}
        req_msg = {'error' : 'false', 
                   'encrypted' : 'false', 
                   'key' : 'false',
                   'value' : json.dumps(data)}
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
        #if response_text['error']:
        #    print 'content error'
        #    print response_text
        #    log.remote_status = False
        #    return
        
        log.remote_status = True
