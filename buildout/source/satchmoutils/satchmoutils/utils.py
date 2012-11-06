from django.conf import settings
from livesettings import config_value
from satchmo_store.shop.models import Config

import re

def slugify(s, num_chars=50): 
    ''' 
    Changes, e.g., "Petty theft" to "petty-theft". 
    This function is the Python equivalent of the javascript function 
    of the same name in django/contrib/admin/media/js/urlify.js. 
    It can get invoked for any field that has a prepopulate_from 
    attribute defined, although it only really makes sense for 
    SlugFields. 
     
    NOTE: this implementation corresponds to the Python implementation 
          of the same algorithm in django/contrib/admin/media/js/urlify.js 
    ''' 
    # remove all these words from the string before urlifying 
    removelist = ["a", "an", "as", "at", "before", "but", "by", "for", 
                  "from", "is", "in", "into", "like", "of", "off", "on", 
                  "onto", "per", "since", "than", "the", "this", "that", 
                  "to", "up", "via", "with"] 
    ignore_words = '|'.join([r for r in removelist]) 
    ignore_words_pat = re.compile('\b('+ignore_words+')\b', re.I) 
    ignore_chars_pat = re.compile(r'[^-A-Z0-9\s]', re.I) 
    outside_space_pat = re.compile(r'^\s+|\s+$') 
    inside_space_pat = re.compile(r'[-\s]+') 
     
    s = ignore_words_pat.sub('', s)  # remove unimportant words 
    s = ignore_chars_pat.sub('', s)  # remove unneeded chars 
    wordlist = s.split()
    s = ''
    for w in wordlist:
        ns = s + w + ' '
        if len(ns) <= num_chars:
            s = ns
        else:
            break
    s = outside_space_pat.sub('', s) # trim leading/trailing spaces
    s = inside_space_pat.sub('-', s) # convert spaces to hyphens 
    s = s.lower()                    # convert to lowercase 
    return s


class ShopUtils(object):
    """Utility to retrieve the shop configuration.
    """

    def schema(self):
        schema = {
            'shop_name': (
                ('SHOP_CONFIG', 'SHOP_NAME'),
                'store_name'),
            'shop_email': (
                ('SHOP_CONFIG', 'EMAIL'),
                'store_email'),
            'shop_iban': (
                ('SHOP_CONFIG', 'IBAN'),
                None),
            'shop_address': (
                ('SHOP_CONFIG', 'ADDRESS'),
                'street1'),
            'shop_zipcode': (
                ('SHOP_CONFIG', 'ZIP_CODE'),
                'postal_code'),
            'shop_city': (
                ('SHOP_CONFIG', 'CITY'),
                'city'),
            'shop_vat': (
                ('SHOP_CONFIG', 'VAT'),
                None),
            'shop_telephone': (
                ('SHOP_CONFIG', 'TELEPHONE'),
                'phone'),
            'shop_fax': (
                ('SHOP_CONFIG', 'FAX'),
                None)}
        schema.update(getattr(settings, 'SHOP_CONFIG_SCHEMA', {}))
        return schema

    def get_shop_config(self):
        shop_config = Config.objects.get_current()
        schema = self.schema()
        config = {}
        for key in schema.keys():
            config_path, config_attribute = schema[key]
            value = config_value(*config_path)
            if not value and config_attribute is not None:
                value = getattr(shop_config, config_attribute, None)
            config[key] = value
        return config
