from django.conf import settings

from .utils import ShopUtils


import logging

log = logging.getLogger('primifrutti_shop_context')


def shop_configs(request):
    shop_utils = ShopUtils()
    ctx = shop_utils.get_shop_config()
    ctx['debug'] = settings.DEBUG
    return ctx
