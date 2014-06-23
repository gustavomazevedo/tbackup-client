# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Destination'
        db.create_table(u'client_destination', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1024, primary_key=True)),
        ))
        db.send_create_signal(u'client', ['Destination'])

        # Adding model 'Origin'
        db.create_table(u'client_origin', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('remote_id', self.gf('django.db.models.fields.BigIntegerField')()),
        ))
        db.send_create_signal(u'client', ['Origin'])

        # Adding model 'WebServer'
        db.create_table(u'client_webserver', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('apikey', self.gf('django.db.models.fields.TextField')()),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('api_url', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('api_version', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'client', ['WebServer'])

        # Adding model 'Config'
        db.create_table(u'client_config', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('destination', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['client.Destination'], null=True)),
            ('interval', self.gf('django.db.models.fields.IntegerField')()),
            ('last_backup', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'client', ['Config'])

        # Adding model 'BackupStatus'
        db.create_table(u'client_backupstatus', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('executing', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'client', ['BackupStatus'])

        # Adding model 'Log'
        db.create_table(u'client_log', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('destination', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['client.Destination'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('local_status', self.gf('django.db.models.fields.BooleanField')()),
            ('remote_status', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'client', ['Log'])


    def backwards(self, orm):
        # Deleting model 'Destination'
        db.delete_table(u'client_destination')

        # Deleting model 'Origin'
        db.delete_table(u'client_origin')

        # Deleting model 'WebServer'
        db.delete_table(u'client_webserver')

        # Deleting model 'Config'
        db.delete_table(u'client_config')

        # Deleting model 'BackupStatus'
        db.delete_table(u'client_backupstatus')

        # Deleting model 'Log'
        db.delete_table(u'client_log')


    models = {
        u'client.backupstatus': {
            'Meta': {'object_name': 'BackupStatus'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'executing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'client.config': {
            'Meta': {'object_name': 'Config'},
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['client.Destination']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interval': ('django.db.models.fields.IntegerField', [], {}),
            'last_backup': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'client.destination': {
            'Meta': {'ordering': "[u'name']", 'object_name': 'Destination'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'primary_key': 'True'})
        },
        u'client.log': {
            'Meta': {'object_name': 'Log'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['client.Destination']"}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local_status': ('django.db.models.fields.BooleanField', [], {}),
            'remote_status': ('django.db.models.fields.BooleanField', [], {})
        },
        u'client.origin': {
            'Meta': {'object_name': 'Origin'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'remote_id': ('django.db.models.fields.BigIntegerField', [], {})
        },
        u'client.webserver': {
            'Meta': {'object_name': 'WebServer'},
            'api_url': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'api_version': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'apikey': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        }
    }

    complete_apps = ['client']