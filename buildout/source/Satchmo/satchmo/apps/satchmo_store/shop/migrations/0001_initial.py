# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    depends_on = (
        ('product', '0001_initial'),
        ('satchmo_store.contact', '0001_initial'),
    )

    def forwards(self, orm):
        
        # Adding model 'Config'
        db.create_table('shop_config', (
            ('site', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sites.Site'], unique=True, primary_key=True)),
            ('store_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('store_description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('store_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('street1', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('street2', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('postal_code', self.gf('django.db.models.fields.CharField')(max_length=9, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['l10n.Country'])),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('in_country_only', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('sales_country', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='sales_country', null=True, to=orm['l10n.Country'])),
        ))
        db.send_create_signal('shop', ['Config'])

        # Adding M2M table for field shipping_countries on 'Config'
        db.create_table('shop_config_shipping_countries', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('config', models.ForeignKey(orm['shop.config'], null=False)),
            ('country', models.ForeignKey(orm['l10n.country'], null=False))
        ))
        db.create_unique('shop_config_shipping_countries', ['config_id', 'country_id'])

        # Adding model 'Cart'
        db.create_table('shop_cart', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('desc', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('date_time_created', self.gf('django.db.models.fields.DateTimeField')()),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contact.Contact'], null=True, blank=True)),
        ))
        db.send_create_signal('shop', ['Cart'])

        # Adding model 'CartItem'
        db.create_table('shop_cartitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cart', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Cart'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product.Product'])),
            ('quantity', self.gf('django.db.models.fields.DecimalField')(max_digits=18, decimal_places=6)),
        ))
        db.send_create_signal('shop', ['CartItem'])

        # Adding model 'CartItemDetails'
        db.create_table('shop_cartitemdetails', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cartitem', self.gf('django.db.models.fields.related.ForeignKey')(related_name='details', to=orm['shop.CartItem'])),
            ('value', self.gf('django.db.models.fields.TextField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('price_change', self.gf('satchmo_utils.fields.CurrencyField')(null=True, max_digits=6, decimal_places=2, blank=True)),
            ('sort_order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('shop', ['CartItemDetails'])

        # Adding model 'OrderVariable'
        db.create_table('shop_ordervariable', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='variables', to=orm['shop.Order'])),
            ('key', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('shop', ['OrderVariable'])

        # Adding model 'Order'
        db.create_table('shop_order', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contact.Contact'])),
            ('ship_addressee', self.gf('django.db.models.fields.CharField')(max_length=61, blank=True)),
            ('ship_street1', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('ship_street2', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('ship_city', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('ship_state', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('ship_postal_code', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('ship_country', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('bill_addressee', self.gf('django.db.models.fields.CharField')(max_length=61, blank=True)),
            ('bill_street1', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('bill_street2', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('bill_city', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('bill_state', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('bill_postal_code', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('bill_country', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('sub_total', self.gf('satchmo_utils.fields.CurrencyField')(display_decimal=4, null=True, max_digits=18, decimal_places=10, blank=True)),
            ('total', self.gf('satchmo_utils.fields.CurrencyField')(display_decimal=4, null=True, max_digits=18, decimal_places=10, blank=True)),
            ('discount_code', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('discount', self.gf('satchmo_utils.fields.CurrencyField')(null=True, max_digits=18, decimal_places=10, blank=True)),
            ('method', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('shipping_description', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('shipping_method', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('shipping_model', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('shipping_cost', self.gf('satchmo_utils.fields.CurrencyField')(null=True, max_digits=18, decimal_places=10, blank=True)),
            ('shipping_discount', self.gf('satchmo_utils.fields.CurrencyField')(null=True, max_digits=18, decimal_places=10, blank=True)),
            ('tax', self.gf('satchmo_utils.fields.CurrencyField')(null=True, max_digits=18, decimal_places=10, blank=True)),
            ('time_stamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
        ))
        db.send_create_signal('shop', ['Order'])

        # Adding model 'OrderItem'
        db.create_table('shop_orderitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Order'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product.Product'])),
            ('quantity', self.gf('django.db.models.fields.DecimalField')(max_digits=18, decimal_places=6)),
            ('unit_price', self.gf('satchmo_utils.fields.CurrencyField')(max_digits=18, decimal_places=10)),
            ('unit_tax', self.gf('satchmo_utils.fields.CurrencyField')(default='0.00', max_digits=18, decimal_places=10)),
            ('line_item_price', self.gf('satchmo_utils.fields.CurrencyField')(max_digits=18, decimal_places=10)),
            ('tax', self.gf('satchmo_utils.fields.CurrencyField')(default='0.00', max_digits=18, decimal_places=10)),
            ('expire_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('completed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('discount', self.gf('satchmo_utils.fields.CurrencyField')(null=True, max_digits=18, decimal_places=10, blank=True)),
        ))
        db.send_create_signal('shop', ['OrderItem'])

        # Adding model 'OrderItemDetail'
        db.create_table('shop_orderitemdetail', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.OrderItem'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('price_change', self.gf('satchmo_utils.fields.CurrencyField')(null=True, max_digits=18, decimal_places=10, blank=True)),
            ('sort_order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('shop', ['OrderItemDetail'])

        # Adding model 'OrderStatus'
        db.create_table('shop_orderstatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Order'])),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('notes', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('time_stamp', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('shop', ['OrderStatus'])

        # Adding model 'OrderAuthorization'
        db.create_table('shop_orderauthorization', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('payment', self.gf('django.db.models.fields.CharField')(max_length=25, blank=True)),
            ('amount', self.gf('satchmo_utils.fields.CurrencyField')(null=True, max_digits=18, decimal_places=10, blank=True)),
            ('time_stamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('transaction_id', self.gf('django.db.models.fields.CharField')(max_length=45, null=True, blank=True)),
            ('details', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='authorizations', to=orm['shop.Order'])),
            ('capture', self.gf('django.db.models.fields.related.ForeignKey')(related_name='authorizations', to=orm['shop.OrderPayment'])),
            ('complete', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('shop', ['OrderAuthorization'])

        # Adding model 'OrderPayment'
        db.create_table('shop_orderpayment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('payment', self.gf('django.db.models.fields.CharField')(max_length=25, blank=True)),
            ('amount', self.gf('satchmo_utils.fields.CurrencyField')(null=True, max_digits=18, decimal_places=10, blank=True)),
            ('time_stamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('transaction_id', self.gf('django.db.models.fields.CharField')(max_length=45, null=True, blank=True)),
            ('details', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payments', to=orm['shop.Order'])),
        ))
        db.send_create_signal('shop', ['OrderPayment'])

        # Adding model 'OrderPendingPayment'
        db.create_table('shop_orderpendingpayment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('payment', self.gf('django.db.models.fields.CharField')(max_length=25, blank=True)),
            ('amount', self.gf('satchmo_utils.fields.CurrencyField')(null=True, max_digits=18, decimal_places=10, blank=True)),
            ('time_stamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('transaction_id', self.gf('django.db.models.fields.CharField')(max_length=45, null=True, blank=True)),
            ('details', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pendingpayments', to=orm['shop.Order'])),
            ('capture', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pendingpayments', to=orm['shop.OrderPayment'])),
        ))
        db.send_create_signal('shop', ['OrderPendingPayment'])

        # Adding model 'OrderPaymentFailure'
        db.create_table('shop_orderpaymentfailure', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('payment', self.gf('django.db.models.fields.CharField')(max_length=25, blank=True)),
            ('amount', self.gf('satchmo_utils.fields.CurrencyField')(null=True, max_digits=18, decimal_places=10, blank=True)),
            ('time_stamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('transaction_id', self.gf('django.db.models.fields.CharField')(max_length=45, null=True, blank=True)),
            ('details', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('reason_code', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='paymentfailures', null=True, to=orm['shop.Order'])),
        ))
        db.send_create_signal('shop', ['OrderPaymentFailure'])

        # Adding model 'OrderTaxDetail'
        db.create_table('shop_ordertaxdetail', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='taxes', to=orm['shop.Order'])),
            ('method', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('tax', self.gf('satchmo_utils.fields.CurrencyField')(null=True, max_digits=18, decimal_places=10, blank=True)),
        ))
        db.send_create_signal('shop', ['OrderTaxDetail'])


    def backwards(self, orm):
        
        # Deleting model 'Config'
        db.delete_table('shop_config')

        # Removing M2M table for field shipping_countries on 'Config'
        db.delete_table('shop_config_shipping_countries')

        # Deleting model 'Cart'
        db.delete_table('shop_cart')

        # Deleting model 'CartItem'
        db.delete_table('shop_cartitem')

        # Deleting model 'CartItemDetails'
        db.delete_table('shop_cartitemdetails')

        # Deleting model 'OrderVariable'
        db.delete_table('shop_ordervariable')

        # Deleting model 'Order'
        db.delete_table('shop_order')

        # Deleting model 'OrderItem'
        db.delete_table('shop_orderitem')

        # Deleting model 'OrderItemDetail'
        db.delete_table('shop_orderitemdetail')

        # Deleting model 'OrderStatus'
        db.delete_table('shop_orderstatus')

        # Deleting model 'OrderAuthorization'
        db.delete_table('shop_orderauthorization')

        # Deleting model 'OrderPayment'
        db.delete_table('shop_orderpayment')

        # Deleting model 'OrderPendingPayment'
        db.delete_table('shop_orderpendingpayment')

        # Deleting model 'OrderPaymentFailure'
        db.delete_table('shop_orderpaymentfailure')

        # Deleting model 'OrderTaxDetail'
        db.delete_table('shop_ordertaxdetail')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contact.contact': {
            'Meta': {'object_name': 'Contact'},
            'create_date': ('django.db.models.fields.DateField', [], {}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '500', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contact.Organization']", 'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contact.ContactRole']", 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'contact.contactorganization': {
            'Meta': {'object_name': 'ContactOrganization'},
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'contact.contactorganizationrole': {
            'Meta': {'object_name': 'ContactOrganizationRole'},
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'contact.contactrole': {
            'Meta': {'object_name': 'ContactRole'},
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'contact.organization': {
            'Meta': {'object_name': 'Organization'},
            'create_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contact.ContactOrganizationRole']", 'null': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contact.ContactOrganization']", 'null': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'l10n.country': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Country'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'admin_area': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'continent': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso2_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            'iso3_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'numcode': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'printable_name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'product.category': {
            'Meta': {'ordering': "['site', 'parent__id', 'ordering', 'name']", 'unique_together': "(('site', 'slug'),)", 'object_name': 'Category'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'meta': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'child'", 'null': 'True', 'to': "orm['product.Category']"}),
            'related_categories': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'related_categories_rel_+'", 'null': 'True', 'to': "orm['product.Category']"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'})
        },
        'product.product': {
            'Meta': {'ordering': "('site', 'ordering', 'name')", 'unique_together': "(('site', 'sku'), ('site', 'slug'))", 'object_name': 'Product'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'also_purchased': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'also_purchased_rel_+'", 'null': 'True', 'to': "orm['product.Product']"}),
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.Category']", 'symmetrical': 'False', 'blank': 'True'}),
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
            'related_items': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'related_items_rel_+'", 'null': 'True', 'to': "orm['product.Product']"}),
            'shipclass': ('django.db.models.fields.CharField', [], {'default': "'DEFAULT'", 'max_length': '10'}),
            'short_description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'sku': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'taxClass': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.TaxClass']", 'null': 'True', 'blank': 'True'}),
            'taxable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'total_sold': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '18', 'decimal_places': '6'}),
            'weight': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'weight_units': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'width_units': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'})
        },
        'product.taxclass': {
            'Meta': {'object_name': 'TaxClass'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'shop.cart': {
            'Meta': {'object_name': 'Cart'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contact.Contact']", 'null': 'True', 'blank': 'True'}),
            'date_time_created': ('django.db.models.fields.DateTimeField', [], {}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"})
        },
        'shop.cartitem': {
            'Meta': {'ordering': "('id',)", 'object_name': 'CartItem'},
            'cart': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Cart']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.Product']"}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'max_digits': '18', 'decimal_places': '6'})
        },
        'shop.cartitemdetails': {
            'Meta': {'ordering': "('sort_order',)", 'object_name': 'CartItemDetails'},
            'cartitem': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'details'", 'to': "orm['shop.CartItem']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'price_change': ('satchmo_utils.fields.CurrencyField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'shop.config': {
            'Meta': {'object_name': 'Config'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['l10n.Country']"}),
            'in_country_only': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True', 'blank': 'True'}),
            'sales_country': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sales_country'", 'null': 'True', 'to': "orm['l10n.Country']"}),
            'shipping_countries': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'shop_configs'", 'blank': 'True', 'to': "orm['l10n.Country']"}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sites.Site']", 'unique': 'True', 'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'store_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'store_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'store_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'street1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'street2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'shop.order': {
            'Meta': {'object_name': 'Order'},
            'bill_addressee': ('django.db.models.fields.CharField', [], {'max_length': '61', 'blank': 'True'}),
            'bill_city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'bill_country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'bill_postal_code': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'bill_state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'bill_street1': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'bill_street2': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contact.Contact']"}),
            'discount': ('satchmo_utils.fields.CurrencyField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'}),
            'discount_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ship_addressee': ('django.db.models.fields.CharField', [], {'max_length': '61', 'blank': 'True'}),
            'ship_city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'ship_country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'ship_postal_code': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'ship_state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'ship_street1': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'ship_street2': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'shipping_cost': ('satchmo_utils.fields.CurrencyField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'}),
            'shipping_description': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'shipping_discount': ('satchmo_utils.fields.CurrencyField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'}),
            'shipping_method': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'shipping_model': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'sub_total': ('satchmo_utils.fields.CurrencyField', [], {'display_decimal': '4', 'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'}),
            'tax': ('satchmo_utils.fields.CurrencyField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'}),
            'time_stamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'total': ('satchmo_utils.fields.CurrencyField', [], {'display_decimal': '4', 'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'})
        },
        'shop.orderauthorization': {
            'Meta': {'object_name': 'OrderAuthorization'},
            'amount': ('satchmo_utils.fields.CurrencyField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'}),
            'capture': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'authorizations'", 'to': "orm['shop.OrderPayment']"}),
            'complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'details': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'authorizations'", 'to': "orm['shop.Order']"}),
            'payment': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'reason_code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'time_stamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '45', 'null': 'True', 'blank': 'True'})
        },
        'shop.orderitem': {
            'Meta': {'ordering': "('id',)", 'object_name': 'OrderItem'},
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'discount': ('satchmo_utils.fields.CurrencyField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'}),
            'expire_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_item_price': ('satchmo_utils.fields.CurrencyField', [], {'max_digits': '18', 'decimal_places': '10'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Order']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.Product']"}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'max_digits': '18', 'decimal_places': '6'}),
            'tax': ('satchmo_utils.fields.CurrencyField', [], {'default': "'0.00'", 'max_digits': '18', 'decimal_places': '10'}),
            'unit_price': ('satchmo_utils.fields.CurrencyField', [], {'max_digits': '18', 'decimal_places': '10'}),
            'unit_tax': ('satchmo_utils.fields.CurrencyField', [], {'default': "'0.00'", 'max_digits': '18', 'decimal_places': '10'})
        },
        'shop.orderitemdetail': {
            'Meta': {'ordering': "('sort_order',)", 'object_name': 'OrderItemDetail'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.OrderItem']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'price_change': ('satchmo_utils.fields.CurrencyField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'shop.orderpayment': {
            'Meta': {'object_name': 'OrderPayment'},
            'amount': ('satchmo_utils.fields.CurrencyField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'}),
            'details': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': "orm['shop.Order']"}),
            'payment': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'reason_code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'time_stamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '45', 'null': 'True', 'blank': 'True'})
        },
        'shop.orderpaymentfailure': {
            'Meta': {'object_name': 'OrderPaymentFailure'},
            'amount': ('satchmo_utils.fields.CurrencyField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'}),
            'details': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paymentfailures'", 'null': 'True', 'to': "orm['shop.Order']"}),
            'payment': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'reason_code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'time_stamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '45', 'null': 'True', 'blank': 'True'})
        },
        'shop.orderpendingpayment': {
            'Meta': {'object_name': 'OrderPendingPayment'},
            'amount': ('satchmo_utils.fields.CurrencyField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'}),
            'capture': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pendingpayments'", 'to': "orm['shop.OrderPayment']"}),
            'details': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pendingpayments'", 'to': "orm['shop.Order']"}),
            'payment': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'reason_code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'time_stamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '45', 'null': 'True', 'blank': 'True'})
        },
        'shop.orderstatus': {
            'Meta': {'ordering': "('time_stamp',)", 'object_name': 'OrderStatus'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Order']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'time_stamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'shop.ordertaxdetail': {
            'Meta': {'ordering': "('id',)", 'object_name': 'OrderTaxDetail'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taxes'", 'to': "orm['shop.Order']"}),
            'tax': ('satchmo_utils.fields.CurrencyField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'})
        },
        'shop.ordervariable': {
            'Meta': {'ordering': "('key',)", 'object_name': 'OrderVariable'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'variables'", 'to': "orm['shop.Order']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['shop']
