# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Origin.auth_token'
        db.add_column(u'client_origin', 'auth_token',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=64),
                      keep_default=False)

        # Adding field 'Backup.remote_id'
        db.add_column(u'client_backup', 'remote_id',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0),
                      keep_default=False)

        # Deleting field 'WebServer.url'
        db.delete_column(u'client_webserver', 'url')

        # Deleting field 'WebServer.api_url'
        db.delete_column(u'client_webserver', 'api_url')

        # Deleting field 'WebServer.apikey'
        db.delete_column(u'client_webserver', 'apikey')

        # Deleting field 'WebServer.api_version'
        db.delete_column(u'client_webserver', 'api_version')

        # Adding field 'WebServer.host'
        db.add_column(u'client_webserver', 'host',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=1024),
                      keep_default=False)

        # Adding field 'WebServer.api_root'
        db.add_column(u'client_webserver', 'api_root',
                      self.gf('django.db.models.fields.CharField')(default='/', max_length=1024),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Origin.auth_token'
        db.delete_column(u'client_origin', 'auth_token')

        # Deleting field 'Backup.remote_id'
        db.delete_column(u'client_backup', 'remote_id')


        # User chose to not deal with backwards NULL issues for 'WebServer.url'
        raise RuntimeError("Cannot reverse this migration. 'WebServer.url' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'WebServer.url'
        db.add_column(u'client_webserver', 'url',
                      self.gf('django.db.models.fields.CharField')(max_length=1024),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'WebServer.api_url'
        raise RuntimeError("Cannot reverse this migration. 'WebServer.api_url' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'WebServer.api_url'
        db.add_column(u'client_webserver', 'api_url',
                      self.gf('django.db.models.fields.CharField')(max_length=1024),
                      keep_default=False)

        # Adding field 'WebServer.apikey'
        db.add_column(u'client_webserver', 'apikey',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'WebServer.api_version'
        raise RuntimeError("Cannot reverse this migration. 'WebServer.api_version' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'WebServer.api_version'
        db.add_column(u'client_webserver', 'api_version',
                      self.gf('django.db.models.fields.CharField')(max_length=20),
                      keep_default=False)

        # Deleting field 'WebServer.host'
        db.delete_column(u'client_webserver', 'host')

        # Deleting field 'WebServer.api_root'
        db.delete_column(u'client_webserver', 'api_root')


    models = {
        'client.backup': {
            'Meta': {'object_name': 'Backup'},
            'destination_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'default': "'SCHEDULED'", 'max_length': '13'}),
            'last_error': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'local_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'remote_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'schedule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['client.Schedule']"}),
            'size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'IDLE'", 'max_length': '13'}),
            'time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'client.destination': {
            'Meta': {'ordering': "[u'name']", 'object_name': 'Destination'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'primary_key': 'True'})
        },
        'client.oplog': {
            'Meta': {'object_name': 'OpLog'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'client.origin': {
            'Meta': {'object_name': 'Origin'},
            'auth_token': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
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
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['client.Destination']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['client.RRule']", 'null': 'True', 'blank': 'True'}),
            'schedule_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'client.webserver': {
            'Meta': {'object_name': 'WebServer'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'api_root': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        }
    }

    complete_apps = ['client']