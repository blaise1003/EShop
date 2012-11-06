# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding index on 'ProductPriceLookup', fields ['productslug']
        db.create_index('product_productpricelookup', ['productslug'])


    def backwards(self, orm):
        
        # Removing index on 'ProductPriceLookup', fields ['productslug']
        db.delete_index('product_productpricelookup', ['productslug'])


    models = {
        'product.attributeoption': {
            'Meta': {'ordering': "('sort_order',)", 'object_name': 'AttributeOption'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'error_message': ('django.db.models.fields.CharField', [], {'default': "u'Invalid Entry'", 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'validation': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'product.category': {
            'Meta': {'ordering': "['site', 'parent__id', 'ordering', 'name']", 'unique_together': "(('site', 'slug'),)", 'object_name': 'Category'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'meta': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'child'", 'blank': 'True', 'null': 'True', 'to': "orm['product.Category']"}),
            'related_categories': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'related_categories_rel_+'", 'blank': 'True', 'null': 'True', 'to': "orm['product.Category']"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'})
        },
        'product.categoryattribute': {
            'Meta': {'ordering': "('option__sort_order',)", 'object_name': 'CategoryAttribute'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.AttributeOption']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'product.categoryimage': {
            'Meta': {'ordering': "['sort']", 'unique_together': "(('category', 'sort'),)", 'object_name': 'CategoryImage'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'blank': 'True', 'null': 'True', 'to': "orm['product.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'picture': ('satchmo_utils.thumbnail.field.ImageWithThumbnailField', [], {'name_field': "'_filename'", 'max_length': '200'}),
            'sort': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'product.categoryimagetranslation': {
            'Meta': {'ordering': "('categoryimage', 'caption', 'languagecode')", 'unique_together': "(('categoryimage', 'languagecode', 'version'),)", 'object_name': 'CategoryImageTranslation'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'categoryimage': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.CategoryImage']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.categorytranslation': {
            'Meta': {'ordering': "('category', 'name', 'languagecode')", 'unique_together': "(('category', 'languagecode', 'version'),)", 'object_name': 'CategoryTranslation'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.Category']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.discount': {
            'Meta': {'object_name': 'Discount'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allValid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allowedUses': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'amount': ('satchmo_utils.fields.CurrencyField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'automatic': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'endDate': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minOrder': ('satchmo_utils.fields.CurrencyField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'numUses': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'percentage': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'shipping': ('django.db.models.fields.CharField', [], {'default': "'NONE'", 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'startDate': ('django.db.models.fields.DateField', [], {}),
            'valid_categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.Category']", 'null': 'True', 'blank': 'True'}),
            'valid_products': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.Product']", 'null': 'True', 'blank': 'True'})
        },
        'product.option': {
            'Meta': {'ordering': "('option_group', 'sort_order', 'name')", 'unique_together': "(('option_group', 'value'),)", 'object_name': 'Option'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'option_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.OptionGroup']"}),
            'price_change': ('satchmo_utils.fields.CurrencyField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '6', 'blank': 'True'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'product.optiongroup': {
            'Meta': {'ordering': "['sort_order', 'name']", 'object_name': 'OptionGroup'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'product.optiongrouptranslation': {
            'Meta': {'ordering': "('optiongroup', 'name', 'languagecode')", 'unique_together': "(('optiongroup', 'languagecode', 'version'),)", 'object_name': 'OptionGroupTranslation'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'optiongroup': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.OptionGroup']"}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.optiontranslation': {
            'Meta': {'ordering': "('option', 'name', 'languagecode')", 'unique_together': "(('option', 'languagecode', 'version'),)", 'object_name': 'OptionTranslation'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.Option']"}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.price': {
            'Meta': {'ordering': "['expires', '-quantity']", 'unique_together': "(('product', 'quantity', 'expires'),)", 'object_name': 'Price'},
            'expires': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('satchmo_utils.fields.CurrencyField', [], {'max_digits': '14', 'decimal_places': '6'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.Product']"}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'default': "'1.0'", 'max_digits': '18', 'decimal_places': '6'})
        },
        'product.product': {
            'Meta': {'ordering': "('site', 'ordering', 'name')", 'unique_together': "(('site', 'sku'), ('site', 'slug'))", 'object_name': 'Product'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'also_purchased': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'also_purchased_rel_+'", 'blank': 'True', 'null': 'True', 'to': "orm['product.Product']"}),
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.Category']", 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'height': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'height_units': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items_in_stock': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '18', 'decimal_places': '6'}),
            'length': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'length_units': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'meta': ('django.db.models.fields.TextField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'related_items': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'related_items_rel_+'", 'blank': 'True', 'null': 'True', 'to': "orm['product.Product']"}),
            'shipclass': ('django.db.models.fields.CharField', [], {'default': "'DEFAULT'", 'max_length': '10'}),
            'short_description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'sku': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'taxClass': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.TaxClass']", 'null': 'True', 'blank': 'True'}),
            'taxable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'total_sold': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '18', 'decimal_places': '6'}),
            'weight': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'weight_units': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'width_units': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'})
        },
        'product.productattribute': {
            'Meta': {'ordering': "('option__sort_order',)", 'object_name': 'ProductAttribute'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.AttributeOption']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.Product']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'product.productimage': {
            'Meta': {'ordering': "['sort']", 'object_name': 'ProductImage'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'picture': ('satchmo_utils.thumbnail.field.ImageWithThumbnailField', [], {'name_field': "'_filename'", 'max_length': '200'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.Product']", 'null': 'True', 'blank': 'True'}),
            'sort': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'product.productimagetranslation': {
            'Meta': {'ordering': "('productimage', 'caption', 'languagecode')", 'unique_together': "(('productimage', 'languagecode', 'version'),)", 'object_name': 'ProductImageTranslation'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'productimage': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.ProductImage']"}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.productpricelookup': {
            'Meta': {'object_name': 'ProductPriceLookup'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'discountable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items_in_stock': ('django.db.models.fields.DecimalField', [], {'max_digits': '18', 'decimal_places': '6'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True'}),
            'parentid': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '6'}),
            'productslug': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'max_digits': '18', 'decimal_places': '6'}),
            'siteid': ('django.db.models.fields.IntegerField', [], {})
        },
        'product.producttranslation': {
            'Meta': {'ordering': "('product', 'name', 'languagecode')", 'unique_together': "(('product', 'languagecode', 'version'),)", 'object_name': 'ProductTranslation'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.Product']"}),
            'short_description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.taxclass': {
            'Meta': {'object_name': 'TaxClass'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['product']
