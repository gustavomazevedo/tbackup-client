# -*- coding: utf-8 -*-

import os
import json
import gzip
import requests
import pytz

from datetime    import datetime, timedelta
from Crypto.Hash import SHA
from StringIO import StringIO

from client.conf.settings import TBACKUP_DATETIME_FORMAT, settings
from django.utils import timezone
from django.core.management import call_command
from django.core.management.base import BaseCommand, make_option
from django.db.models import F, Q
from client.models import (
    Origin,
    WebServer,
    Backup,
    Schedule,
)
from client.handlers import DataHandler
from client import functions

TBACKUP_DUMP_DIR = settings.TBACKUP_DUMP_DIR
    

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '--backup-trigger',
            '-b',
            action='store_true',
            dest  ='trigger_backups',
            help  =('Backs up data and sends backups across server if '
            'it''s scheduled to run at the date and time of execution of this script')
        ),
        make_option(
            '--retry-backup',
            '-r',
            action='store_true',
            dest  ='retry_failed_backups',
            help  ='Retry backing up (locally) failed past attempts'
        ),
        make_option(
            '--send-backups',
            '-s',
            action='store_true',
            dest  ='send_unsent_backups',
            help  ='Send unsent backups to WebServer'
        ),
        make_option(
            '--all-tasks',
            '-a',
            action='store_true',
            dest  ='all_missing_tasks',
            help  ='Runs -r and then -s'
        ),
    )

    def handle(self, *args, **options):
        #try:
            #Don't accept commands if origin is not registered
            if not Origin.objects.exists():
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
        #self.schedule_missing_jobs()
        self.retry_failed_backups()
        self.send_unsent_backups()

    #def schedule_missing_jobs(self):
    #    """
    #    Schedule missing future jobs (in case of failure in the past)
    #    Recommended to run as a hourly periodic task
    #    """
    #    #get all active schedules
    #    schedules = Schedule.objects.filter(active=True)
    #    #get all future jobs
    #    backup_jobs = Backup.objects.filter(time__gte=timezone.now())
    #    #filter next run for all future jobs
    #    b_initial_times = (b.schedule.next_runtime() for b in backup_jobs)
    #    #filter unscheduled jobs
    #    unscheduled = (s for s in schedules if s.next_runtime() not in b_initial_times)
    #    #schedule all missing jobs
    #    for u in unscheduled:
    #        Backup.objects.create(schedule=u,
    #                              time=u.next_runtime())

    def send_unsent_backups(self):
        """
        Send unsent backups to WebServer
        Recommended to run as a hourly periodic task
        """
        for unsent in Backup.objects.filter(Q(state=Backup.WAITING) |
                                            Q(state=Backup.ERROR_SENDING)):
            unsent.send(WebServer.instance())

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
        if not WebServer.objects.exists():
            raise Exception(_('WebServer does not exist'))
        if not Origin.objects.exists():
            raise Exception(_('Origin does not exist'))
        
        handler = DataHandler(origin=Origin.instance(),webserver=WebServer.instance())
        if len(handler.schedules) == 0: return
        
        handler.cache_dumpdata()
        for s in handler.schedules:
            handler.backup(schedule=s)
            
        
#def fill_data():
#    from dummy_app.models import DummyData
#    for i in xrange(5):
#        DummyData.objects.create( name='name %i' %i,
#                                  type='type %i' %i )
