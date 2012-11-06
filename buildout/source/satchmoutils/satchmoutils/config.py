from livesettings import config_register, ConfigurationGroup, StringValue
from django.core.validators import RegexValidator, validate_email
from django.utils.translation import ugettext_lazy as _


class IBANValue(StringValue):

    def make_field(self, **kwargs):
        validators = kwargs.setdefault('validators', [])
        validators.append(
            RegexValidator(
                (r'[a-zA-Z]{2}[0-9]{2}[a-zA-Z0-9]{4}[0-9]{7}'
                 r'([a-zA-Z0-9]?){0,16}'),
                message=_(u"Invalid IBAN code. Please make sure to remove "
                          u"all spaces")))
        return super(IBANValue, self).make_field(**kwargs)


class EmailValue(StringValue):

    def make_field(self, **kwargs):
        validators = kwargs.setdefault('validators', [])
        validators.append(validate_email)
        return super(EmailValue, self).make_field(**kwargs)


SHOP_CONFIG = ConfigurationGroup(
    'SHOP_CONFIG',
    _(u'Shop configuration'),
    ordering=0)

config_register(
    StringValue(
        SHOP_CONFIG,
        'SHOP_NAME',
        description=_(u'Shop name'),
        help_text=_(u'The name of the site, shown on all pages and mails'),
        default=u"Sho Name"))

config_register(
    IBANValue(
        SHOP_CONFIG,
        'IBAN',
        description=_(u'IBAN'),
        help_text=_(u'your bank account code: fill in if you have chosen '
                    u'to accept payments via bank transfer'),
        default=u''))

config_register(
    StringValue(
        SHOP_CONFIG,
        'ADDRESS',
        description=_(u'Address'),
        help_text=_(u'the physical or legal address of your business'),
        default=u"address"))

config_register(
    StringValue(
        SHOP_CONFIG,
        'ZIP_CODE',
        description=_(u'Zip code'),
        help_text=_(u'the zip code of the shop address'),
        default=u"00000"))

config_register(
    StringValue(
        SHOP_CONFIG,
        'CITY',
        description=_(u'City'),
        help_text=_(u'the city of the shop'),
        default=u"city"))

config_register(
    EmailValue(
        SHOP_CONFIG,
        'EMAIL',
        description=_(u'E-mail'),
        help_text=_(u"an e-mail address where your customers can "
                    u"contact you for informations or other needs"),
        default="email@domain.ext"))

config_register(
    StringValue(
        SHOP_CONFIG,
        'VAT',
        description=_(u'Vat number'),
        help_text=_(u'shop vat number'),
        default=u"P.IVA 12345678910"))

config_register(
    StringValue(
        SHOP_CONFIG,
        'TELEPHONE',
        description=_(u'Telephone'),
        help_text=_(u"a phone number to allow your customers to contact you"),
        default=u"0000000000"))

config_register(
    StringValue(
        SHOP_CONFIG,
        'FAX',
        description=_(u'Fax'),
        help_text=_(u"a fax number to allow your customers to contact you"),
        default=u"0000000000"))
