# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Backup'
        db.create_table(u'client_backup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('schedule', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['client.Schedule'])),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
            ('local_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
            ('size', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
            ('destination_name', self.gf('django.db.models.fields.CharField')(max_length=256, null=True)),
            ('kind', self.gf('django.db.models.fields.CharField')(default='SCHEDULED', max_length=13)),
            ('state', self.gf('django.db.models.fields.CharField')(default='IDLE', max_length=13)),
            ('last_error', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal('client', ['Backup'])

        # Adding model 'OpLog'
        db.create_table(u'client_oplog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('client', ['OpLog'])

        # Adding model 'RRule'
        db.create_table(u'client_rrule', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('frequency', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('params', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('client', ['RRule'])

        # Adding model 'Schedule'
        db.create_table(u'client_schedule', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('destination', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['client.Destination'], null=True)),
            ('schedule_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('rule', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['client.RRule'], null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('client', ['Schedule'])

        # Adding model 'Destination'
        db.create_table(u'client_destination', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1024, primary_key=True)),
        ))
        db.send_create_signal('client', ['Destination'])

        # Adding model 'Origin'
        db.create_table(u'client_origin', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('remote_id', self.gf('django.db.models.fields.BigIntegerField')()),
        ))
        db.send_create_signal('client', ['Origin'])

        # Adding model 'WebServer'
        db.create_table(u'client_webserver', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('apikey', self.gf('django.db.models.fields.TextField')()),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('api_url', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('api_version', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('client', ['WebServer'])


    def backwards(self, orm):
        # Deleting model 'Backup'
        db.delete_table(u'client_backup')

        # Deleting model 'OpLog'
        db.delete_table(u'client_oplog')

        # Deleting model 'RRule'
        db.delete_table(u'client_rrule')

        # Deleting model 'Schedule'
        db.delete_table(u'client_schedule')

        # Deleting model 'Destination'
        db.delete_table(u'client_destination')

        # Deleting model 'Origin'
        db.delete_table(u'client_origin')

        # Deleting model 'WebServer'
        db.delete_table(u'client_webserver')


    models = {
        'client.backup': {
            'Meta': {'object_name': 'Backup'},
            'destination_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'default': "'SCHEDULED'", 'max_length': '13'}),
            'last_error': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'local_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
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