# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'BackupStatus'
        db.delete_table(u'client_backupstatus')

        # Deleting model 'Log'
        db.delete_table(u'client_log')

        # Deleting model 'LocalBackupQueue'
        db.delete_table(u'client_localbackupqueue')

        # Deleting field 'Backup.local_name'
        db.delete_column(u'client_backup', 'local_name')

        # Adding field 'Backup.name'
        db.add_column(u'client_backup', 'name',
                      self.gf('django.db.models.fields.CharField')(default=u'-', max_length=256),
                      keep_default=False)


        # Changing field 'Backup.kind'
        db.alter_column(u'client_backup', 'kind', self.gf('django.db.models.fields.CharField')(max_length=13))

        # Changing field 'Backup.state'
        db.alter_column(u'client_backup', 'state', self.gf('django.db.models.fields.CharField')(max_length=13))

        # Changing field 'Backup.destination_name'
        db.alter_column(u'client_backup', 'destination_name', self.gf('django.db.models.fields.CharField')(max_length=256, null=True))

        # Changing field 'Backup.size'
        db.alter_column(u'client_backup', 'size', self.gf('django.db.models.fields.BigIntegerField')(null=True))
        # Adding field 'WebServer.active'
        db.add_column(u'client_webserver', 'active',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'WebServer.creation_date'
        db.add_column(u'client_webserver', 'creation_date',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2014, 8, 11, 0, 0), blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'BackupStatus'
        db.create_table(u'client_backupstatus', (
            ('count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('executing', self.gf('django.db.models.fields.BooleanField')(default=False)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'client', ['BackupStatus'])

        # Adding model 'Log'
        db.create_table(u'client_log', (
            ('remote_status', self.gf('django.db.models.fields.BooleanField')()),
            ('destination', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['client.Destination'])),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('local_status', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'client', ['Log'])

        # Adding model 'LocalBackupQueue'
        db.create_table(u'client_localbackupqueue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'client', ['LocalBackupQueue'])

        # Adding field 'Backup.local_name'
        db.add_column(u'client_backup', 'local_name',
                      self.gf('django.db.models.fields.CharField')(default=u'-', max_length=256),
                      keep_default=False)

        # Deleting field 'Backup.name'
        db.delete_column(u'client_backup', 'name')


        # Changing field 'Backup.kind'
        db.alter_column(u'client_backup', 'kind', self.gf('django.db.models.fields.CharField')(max_length=1))

        # Changing field 'Backup.state'
        db.alter_column(u'client_backup', 'state', self.gf('django.db.models.fields.CharField')(max_length=2))

        # Changing field 'Backup.destination_name'
        db.alter_column(u'client_backup', 'destination_name', self.gf('django.db.models.fields.CharField')(default=u'-', max_length=256))

        # Changing field 'Backup.size'
        db.alter_column(u'client_backup', 'size', self.gf('django.db.models.fields.BigIntegerField')(default=u'-'))
        # Deleting field 'WebServer.active'
        db.delete_column(u'client_webserver', 'active')

        # Deleting field 'WebServer.creation_date'
        db.delete_column(u'client_webserver', 'creation_date')


    models = {
        u'client.backup': {
            'Meta': {'object_name': 'Backup'},
            'destination_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'default': "'SCHEDULED'", 'max_length': '13'}),
            'last_error': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'local_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'schedule': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['client.Schedule']"}),
            'size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'IDLE'", 'max_length': '13'}),
            'time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'client.destination': {
            'Meta': {'ordering': "[u'name']", 'object_name': 'Destination'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'primary_key': 'True'})
        },
        u'client.origin': {
            'Meta': {'object_name': 'Origin'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'remote_id': ('django.db.models.fields.BigIntegerField', [], {})
        },
        u'client.rrule': {
            'Meta': {'object_name': 'RRule'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'params': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'client.schedule': {
            'Meta': {'object_name': 'Schedule'},
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['client.Destination']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rule': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['client.RRule']", 'null': 'True', 'blank': 'True'}),
            'schedule_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'client.webserver': {
            'Meta': {'object_name': 'WebServer'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'api_url': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'api_version': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'apikey': ('django.db.models.fields.TextField', [], {}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        }
    }

    complete_apps = ['client']