# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Backup.destination_name'
        db.delete_column(u'client_backup', 'destination_name')

        # Deleting field 'Backup.kind'
        db.delete_column(u'client_backup', 'kind')

        # Deleting field 'Backup.state'
        db.delete_column(u'client_backup', 'state')

        # Adding field 'Backup.destination'
        db.add_column(u'client_backup', 'destination',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True),
                      keep_default=False)

        # Adding field 'Backup.local_backup_date'
        db.add_column(u'client_backup', 'local_backup_date',
                      self.gf('django.db.models.fields.DateTimeField')(null=True),
                      keep_default=False)

        # Adding field 'Backup.remote_backup_date'
        db.add_column(u'client_backup', 'remote_backup_date',
                      self.gf('django.db.models.fields.DateTimeField')(null=True),
                      keep_default=False)

        # Deleting field 'Schedule.schedule_time'
        db.delete_column(u'client_schedule', 'schedule_time')

        # Adding field 'Schedule.initial_time'
        db.add_column(u'client_schedule', 'initial_time',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 11, 27, 0, 0)),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Backup.destination_name'
        db.add_column(u'client_backup', 'destination_name',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True),
                      keep_default=False)

        # Adding field 'Backup.kind'
        db.add_column(u'client_backup', 'kind',
                      self.gf('django.db.models.fields.CharField')(default='SCHEDULED', max_length=13),
                      keep_default=False)

        # Adding field 'Backup.state'
        db.add_column(u'client_backup', 'state',
                      self.gf('django.db.models.fields.CharField')(default='IDLE', max_length=13),
                      keep_default=False)

        # Deleting field 'Backup.destination'
        db.delete_column(u'client_backup', 'destination')

        # Deleting field 'Backup.local_backup_date'
        db.delete_column(u'client_backup', 'local_backup_date')

        # Deleting field 'Backup.remote_backup_date'
        db.delete_column(u'client_backup', 'remote_backup_date')


        # User chose to not deal with backwards NULL issues for 'Schedule.schedule_time'
        raise RuntimeError("Cannot reverse this migration. 'Schedule.schedule_time' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Schedule.schedule_time'
        db.add_column(u'client_schedule', 'schedule_time',
                      self.gf('django.db.models.fields.DateTimeField')(),
                      keep_default=False)

        # Deleting field 'Schedule.initial_time'
        db.delete_column(u'client_schedule', 'initial_time')


    models = {
        'client.backup': {
            'Meta': {'object_name': 'Backup'},
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_error': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'local_backup_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'local_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'remote_backup_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'remote_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'schedule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['client.Schedule']"}),
            'size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'client.oplog': {
            'Meta': {'object_name': 'OpLog'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'client.origin': {
            'Meta': {'object_name': 'Origin'},
            'auth_token': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'remote_id': ('django.db.models.fields.BigIntegerField', [], {})
        },
        'client.rrule': {
            'Meta': {'object_name': 'RRule'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'params': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'client.schedule': {
            'Meta': {'object_name': 'Schedule'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 11, 27, 0, 0)'}),
            'rule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['client.RRule']", 'null': 'True', 'blank': 'True'})
        },
        'client.webserver': {
            'Meta': {'object_name': 'WebServer'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'api_root': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        }
    }

    complete_apps = ['client']