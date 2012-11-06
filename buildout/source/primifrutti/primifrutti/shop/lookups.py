from product.models import Product
from django.db.models import Q


class ProductLookup(object):
    """The product look up for the autocomplete field
    """

    # pylint: disable=W0613

    def get_query(self, q, request):
        return Product.objects.filter(
            Q(name__istartswith=q) | Q(sku__istartswith=q))

    def format_result(self, product):
        return u"%s (%s)" % (product.name, product.slug)

    def format_item(self, product):
        return u'<b>%s</b> (%s)' % (product.name, product.sku)

    def get_objects(self, ids):
        return Product.objects.filter(pk__in=ids).order_by('name')
