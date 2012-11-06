# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TaxRate'
        db.create_table('noarea_taxrate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('taxClass', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product.TaxClass'])),
            ('percentage', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=6)),
        ))
        db.send_create_signal('noarea', ['TaxRate'])

    def backwards(self, orm):
        # Deleting model 'TaxRate'
        db.delete_table('noarea_taxrate')

    models = {
        'noarea.taxrate': {
            'Meta': {'object_name': 'TaxRate'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percentage': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '6'}),
            'taxClass': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.TaxClass']"})
        },
        'product.taxclass': {
            'Meta': {'object_name': 'TaxClass'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['noarea']