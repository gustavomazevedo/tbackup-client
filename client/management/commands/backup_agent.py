# -*- coding: utf-8 -*-

import os
import json
import gzip
import requests
import pytz

from datetime    import datetime, timedelta
from Crypto.Hash import SHA

from django.conf                 import settings
from django.utils                import timezone
from django.core.management      import call_command
from django.core.management.base import BaseCommand, make_option
from django.db.models            import F, Q
from client.models               import (
                                          Origin,
                                          WebServer,
                                          Backup,
                                          Schedule,
                                        )
from client import functions


TBACKUP_DUMP_DIR = settings.TBACKUP_DUMP_DIR


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--backup-trigger',
                    '-b',
                    action='store_true',
                    dest  ='trigger_backups',
                    help  =('Backs up data and sends backups across server if '
                    'it''s scheduled to run at the date and time of execution')
        ),
        make_option('--schedule-jobs',
                    '-j',
                    action='store_true',
                    dest  ='schedule_missing_jobs',
                    help  ='Schedule missing future jobs (in case of failure in the past)'
        ),
        make_option('--retry-backup',
                    '-r',
                    action='store_true',
                    dest  ='retry_failed_backups',
                    help  ='Retry backing up (locally) failed past attempts'
        ),
        make_option('--send-backups',
                    '-s',
                    action='store_true',
                    dest  ='send_unsent_backups',
                    help  ='Send unsent backups to WebServer'
        ),
        make_option('--all-tasks',
                    '-a',
                    action='store_true',
                    dest  ='all_missing_tasks',
                    help  ='Does -j, -r and then -s'
        ),
        make_option('--update-info',
                    '-u',
                    action='store_true',
                    dest  ='update_info',
                    help  ='Updates info about WebServer and Destination'
        ),
    )
                
    def handle(self, *args, **options):
        #try: 
            #Don't accept commands if origin is not registered
            if not Origin.objects.filter(pk=1).exists():
                return
        
            if options.get('trigger_backups', False):
                self.trigger_backups()
                
        #except Exception, e:
        #    self.stderr.write('%s: %s' % (e.__class__.__name__, e))
        
#    def delete_old_backups(self):
#        fourteen_days_ago = datetime.now() - datetime.timedelta(days=14)
#        backuphistory = Log.objects.filter(
#            local_status=True,
#            remote_status=True,
#            dump_date__lt=fourteen_days_ago)
#        
#        for backup in backuphistory:
#            os.remove(os.path.join(TBACKUP_DUMP_DIR, backup.filename))
#            backup.local_status = False
#            backup.save()
    
    def all_missing_tasks(self):
        self.schedule_missing_jobs()
        self.retry_failed_backups()
        self.send_unsent_backups()
        
    def schedule_missing_jobs(self):
        """
        Schedule missing future jobs (in case of failure in the past)
        Recommended to run as a hourly periodic task
        """
        #get all active schedules
        schedules = Schedule.objects.filter(active=True)
        #get all future jobs
        backup_jobs = Backup.objects.filter(time__gte=timezone.now())
        #filter next run for all future jobs
        b_schedule_times = (b.schedule.next_run() for b in backup_jobs)
        #filter unscheduled jobs
        unscheduled = (s for s in schedules if s.next_run() not in b_schedule_times)
        #schedule all missing jobs
        for u in unscheduled:
            Backup.objects.create(schedule=u,
                                  time=u.next_run())
         
    def send_unsent_backups(self):
        """
        Send unsent backups to WebServer
        Recommended to run as a hourly periodic task
        """
        for unsent in Backup.objects.filter(Q(state=Backup.WAITING) |
                                            Q(state=Backup.ERROR_SENDING)):
            unsent.send(WebServer.get())

    def retry_failed_backups(self):
        """
        Retry backing up (locally) failed past attempts
        Recommended to run as a hourly periodic task
        """
        dt = functions.normalize_time(timezone.now())
        backups = Backup.objects.filter(Q(state=Backup.IDLE) |
                                        Q(state=Backup.ERROR_RUNNING),
                                        time__lte=dt)
        for b in backups:
            b.backup()
    
    
        
    def trigger_backups(self):
        """
        This task will trigger backups to run if it's the scheduled date and time
        """
        #current time
        now = functions.normalize_time(timezone.now())
        self.stdout.write(str(timezone.make_naive(timezone.now(), pytz.timezone(settings.TIME_ZONE))))
        self.stdout.write(str(timezone.make_naive(now, pytz.timezone(settings.TIME_ZONE))))
        #get schedules to run now
        schedules = self.get_schedules_to_run(now)
        self.stdout.write(str(len(schedules)))
        if len(schedules) == 0: return
        
        for s in schedules:
            #get or create job
            backup_job, created = Backup.objects.get_or_create(schedule=s,
                                                           time=now)
            self.stdout.write(str(created))
            #backup
            backup_job.backup()
            #send to WebServer
            backup_job.send(WebServer.get())
            
    def get_schedules_to_run(self, t):
        """
        Fetches all active schedules to run now
        """
        #schedules = Schedule.objects.filter(active=True,
        #                                    schedule_time__hour=t.hour,
        #                                    schedule_time__minute=t.minute)
        #return [s for s in schedules if s.trigger(t)]
        schedules = Schedule.objects.filter(active=True,
                                            schedule_time__hour=t.hour)
        print schedules
        schedules = Schedule.objects.all()
        for s in schedules:
            print t, s.schedule_time
            print t.hour, s.schedule_time.hour
            print t.minute, s.schedule_time.minute
        return [s for s in schedules if s.trigger(t)]

#def fill_data():
#    from dummy_app.models import DummyData
#    for i in xrange(5):
#        DummyData.objects.create( name='name %i' %i,
#                                  type='type %i' %i )
