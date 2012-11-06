import logging
from decimal import Decimal
from django.core.exceptions import ImproperlyConfigured
from livesettings import config_value
from product.models import TaxClass
from satchmo_utils import is_string_like

from satchmoutils.tax.modules.noarea.models import TaxRate


log = logging.getLogger('satchmoutils.tax.noarea')

class Processor(object):
    
    method = "noarea"
    
    def __init__(self, order=None, user=None):
        """
        Any preprocessing steps should go here
        For instance, copying the shipping and billing areas
        """
        self.order = order
        self.user = user
        
    def get_percent(self, taxclass="Default"):
        return 100*self.get_rate(taxclass=taxclass)
        
    def get_rate(self, taxclass=None, get_object=False, **kwargs):
        if not taxclass:
            taxclass = "Default"
        rate = None
            
        if is_string_like(taxclass):
            try:
                taxclass = TaxClass.objects.get(title__iexact=taxclass)
            
            except TaxClass.DoesNotExist:
                raise ImproperlyConfigured("Can't find a '%s' Tax Class", taxclass)
            
        try:
            rate = TaxRate.objects.get(taxClass=taxclass)
            
        except TaxRate.DoesNotExist:
            rate = None
        
        log.debug("Got rate [%s] = %s", taxclass, rate)
        if get_object:
            return rate
        else:
            if rate:
                return rate.percentage
            else:
                return Decimal("0.00")

    def by_price(self, taxclass, price):
        rate = self.get_rate(taxclass)

        if not rate:
            t = Decimal("0.00")
        else:
            t = rate * price

        return t

    def by_product(self, product, quantity=Decimal('1')):
        """Get the tax for a given product"""
        price = product.get_qty_price(quantity)
        tc = product.taxClass
        return self.by_price(tc, price)
        
    def by_orderitem(self, orderitem):
        if orderitem.product.taxable:
            price = orderitem.sub_total
            taxclass = orderitem.product.taxClass
            return self.by_price(taxclass, price)
        else:
            return Decimal("0.00")

    def shipping(self, subtotal=None):
        if subtotal is None and self.order:
            subtotal = self.order.shipping_sub_total

        if subtotal:
            rate = None
            if config_value('TAX','TAX_SHIPPING'):
                try:
                    tc = TaxClass.objects.get(title=config_value('TAX', 'TAX_CLASS'))
                    rate = self.get_rate(taxclass=tc)
                except:
                    log.error("'Shipping' TaxClass doesn't exist.")

            if rate:
                t = rate * subtotal
            else:
                t = Decimal("0.00")
            
        else:
            t = Decimal("0.00")
        
        return t

    def process(self, order=None):
        """
        Calculate the tax and return it.
        
        Probably need to make a breakout.
        """
        if order:
            self.order = order
        else:
            order = self.order
        
        sub_total = Decimal('0.00')
        taxes = {}
        
        rates = {}
        for item in order.orderitem_set.filter(product__taxable=True):
            tc = item.product.taxClass
            if tc:
                tc_key = tc.title
            else:
                tc_key = "Default"
                
            if rates.has_key(tc_key):
                rate = rates[tc_key]
            else:
                rate = self.get_rate(tc, get_object=True)
                rates[tc_key] = rate
                taxes[tc_key] = Decimal("0.00")
            
            if config_value('TAX', 'TAX_USE_ITEMPRICE'):
                # In Europe, if there is a supplier 
                # which applies discounts to products
                # you have to use full price for taxes.
                price = item.line_item_price
            else:
                # use discounted price before taxing
                price = item.sub_total
                
            if rate:
                t = price*rate.percentage
            else:
                t = Decimal("0.00")
            sub_total += t
            taxes[tc_key] += t
        
        ship = self.shipping()
        sub_total += ship
        taxes['Shipping'] = ship
        
        for k in taxes:
            taxes[k] = taxes[k]
        
        return sub_total, taxes
