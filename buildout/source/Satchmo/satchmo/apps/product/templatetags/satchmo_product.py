from django import template
from django.template import Node, Variable
from django.template import TemplateSyntaxError
from livesettings import config_value
from product.models import Product
from product.queries import bestsellers
from satchmo_utils.templatetags import get_filter_args
import keyedcache

register = template.Library()

@register.filter
def best_selling_products_list(count):
    """Get a list of best selling products"""
    try:
        ct = int(count)
    except ValueError:
        ct = config_value('PRODUCT','NUM_PAGINATED')

    return bestsellers(ct)

@register.filter
def recent_products_list(count):
    """Get a list of recent products"""
    try:
        ct = int(count)
    except ValueError:
        ct = config_value('PRODUCT','NUM_PAGINATED')

    query = Product.objects.recent_by_site()
    return query[:ct]

def is_producttype(product, ptype):
    """Returns True if product is ptype"""
    if ptype in product.get_subtypes():
        return True
    else:
        return False

register.filter('is_producttype', is_producttype)

def product_count(category, args=''):
    """Get a count of products for the base object.

    If `category` is None, then count everything.
    If it is a `Category` object then count everything in the category and subcategories.
    """
    args, kwargs = get_filter_args(args, boolargs=('variations'))
    variations = kwargs.get('variations', False)
    try:
        ct = keyedcache.cache_get('product_count', category, variations)
    except keyedcache.NotCachedError:
        if not category:
            ct = Product.objects.active_by_site(variations=variations).count()
        else:
            ct = category.active_products(include_children=True, variations=variations).count()

        keyedcache.cache_set('product_count', category, args, value=ct)
    return ct

register.filter('product_count', product_count)

def product_images(product, args=""):
    args, kwargs = get_filter_args(args,
        keywords=('include_main', 'maximum'),
        boolargs=('include_main'),
        intargs=('maximum'),
        stripquotes=True)

    q = product.productimage_set
    if kwargs.get('include_main', True):
        q = q.all()
    else:
        main = product.main_image
        q = q.exclude(id = main.id)

    maximum = kwargs.get('maximum', -1)
    if maximum>-1:
        q = list(q)[:maximum]

    return q

register.filter('product_images', product_images)

class FeaturedListNode(Node):
    """Template Node tag which pushes the featured product list into the context"""
    def __init__(self, var, nodelist):
        self.var = var
        self.nodelist = nodelist

    def render(self, context):

        prods = Product.objects.featured_by_site()
        context[self.var] = prods

        context.push()
        context[self.var] = prods
        output = self.nodelist.render(context)
        context.pop()
        return output

@register.tag
def product_featured_list(parser, token):
    """Push the featured product list into the context using the given variable name.

    Sample usage::

        {% product_featured_list as var %}

    """
    args = token.split_contents()
    ct = len(args)
    if not ct == 3:
        raise TemplateSyntaxError("%r tag expecting 'as varname', got: %s" % (args[0], args))

    var = args[2]

    nodelist = parser.parse(('endproduct_featured_list',))
    parser.delete_first_token()

    return FeaturedListNode(var, nodelist)

def smart_attr(product, key):
    """
    Run the smart_attr function on the spec'd product
    """
    return product.smart_attr(key)

register.filter('smart_attr', smart_attr)


def product_sort_by_price(products):
    """
    Sort a product list by unit price

    Example::

        {% for product in products|product_sort_by_price %}
    """

    if products:
        fast = [(product.unit_price, product) for product in products]
        fast.sort()
        return zip(*fast)[1]

register.filter('product_sort_by_price', product_sort_by_price)
