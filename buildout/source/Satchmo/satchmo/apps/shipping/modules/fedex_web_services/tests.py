from decimal import Decimal
from django.contrib.sites.models import Site
from django.test import TestCase
from product.models import Product
from satchmo_store.shop.models import Cart, Config
from satchmo_store.contact.models import Contact
from shipping.modules.fedex_web_services.shipper import Shipper, convert_weight
from shipping.modules.fedex_web_services import get_config_obj, get_methods
from livesettings import config_get_group
import keyedcache

class FedexBaseTest(TestCase):

    fixtures = ['l10n-data.yaml','test_shop.yaml', 'sample-store-data.yaml']

    def setUp(self):
        self.site = Site.objects.get_current()
        self.contact = Contact.objects.get(email='chris@aol.com')
        self.config = Config.objects.get_current()
        self.config.postal_code = '12180'
        self.config.save()
        self.prod_counter = 0

    def tearDown(self):
        keyedcache.cache_delete()

    def new_cart(self):
        """
        Creates a new cart for testing.
        """
        cart = Cart.objects.create(site=self.site, customer=self.contact)
        cart.save()
        return cart

    def new_product(self, weight_units, weight=1.0):
        """
        Creates a new product for testing.
        """
        prod = Product.objects.create(
            slug='p%s' % self.prod_counter,
            name='p%s' % self.prod_counter,
            weight=weight,
            weight_units=weight_units,
            site=self.site)
        prod.save()
        self.prod_counter += 1
        return prod

    def new_shipper(self, single_box=True):
        """
        Creates a new Shipper instance, make sure that you set-up your livesettings for this module.
        """
        
        service_type = ('FEDEX_GROUND', 'Fedex Ground Shipping')

        settings = config_get_group('shipping.modules.fedex_web_services')
        CONFIG_OBJ = get_config_obj(settings)
        packaging = settings.PACKAGING.value or "YOUR_PACKAGING"
        default_weight = settings.DEFAULT_ITEM_WEIGHT.value or 0.5
        default_weight_units = settings.DEFAULT_WEIGHT_UNITS.value
        single_box = single_box
        verbose_log = settings.VERBOSE_LOG.value
        dropoff_type = settings.DROPOFF_TYPE.value

        shipper = Shipper(
            service_type=service_type,
            config=CONFIG_OBJ,
            packaging=packaging,
            default_weight=default_weight,
            default_weight_units=default_weight_units,
            single_box=single_box,
            verbose_log=verbose_log,
            dropoff_type=dropoff_type)

        return shipper

    def new_calculated_shipper(self, weight_units, weight=1.0, cart_item_qty=1, single_box=True):
        """
        This returns a shipper, already calculated for a new cart and with cartitems.
        """
        cart = self.new_cart()
        cart_item = cart.add_item(self.new_product(weight_units, weight), cart_item_qty)
        shipper = self.new_shipper(single_box=single_box)
        shipper.calculate(cart, self.contact)
        return shipper

    def test_various_weights(self):
        """
        Checks that we get a decimal value > than 0 from the shipper, when supplied
        with weight units in ('KG', 'OZ', 'LB' and 'G' in both lower and upper case.)
        """
        assert(self.new_calculated_shipper('KG').cost() > Decimal("0.00"))
        assert(self.new_calculated_shipper('OZ').cost() > Decimal("0.00"))
        assert(self.new_calculated_shipper('LB').cost() > Decimal("0.00"))
        assert(self.new_calculated_shipper('G').cost() > Decimal("0.00"))
        assert(self.new_calculated_shipper('kg').cost() > Decimal("0.00"))
        assert(self.new_calculated_shipper('oz').cost() > Decimal("0.00"))
        assert(self.new_calculated_shipper('lb').cost() > Decimal("0.00"))
        assert(self.new_calculated_shipper('g').cost() > Decimal("0.00"))

    def test_single_box_false(self):
        """
        Checks that we get a valid cost with single_box as False, and few lineitems.
        """
        cart = self.new_cart()
        cart_item1 = cart.add_item(self.new_product('KG', 1.0), 2)
        cart_item2 = cart.add_item(self.new_product('KG', 1.0), 2)
        shipper = self.new_shipper(single_box=False)
        shipper.calculate(cart, self.contact)
        assert(shipper.cost() > Decimal("0.00"))

    def test_value_is_same(self):
        """
        Checks that we can supply oz, g, lb and kg to the shipper calculate,
        and that the rate result is the same.
        """
        assert(
            self.new_calculated_shipper('g', convert_weight(1, 'kg', 'g')).cost() ==
            self.new_calculated_shipper('oz', convert_weight(1, 'kg', 'oz')).cost() ==
            self.new_calculated_shipper('lb', convert_weight(1, 'kg', 'lb')).cost() ==
            self.new_calculated_shipper('kg', convert_weight(1, 'kg', 'kg')).cost())
