import re
from django.utils.encoding import smart_unicode
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class BaseValidator(object):

    def __init__(self, message = u"Invalid", code = 'invalid'):
        self.message = message
        self.code = code

    def __call__(self, value):
        if not self.is_valid(smart_unicode(value)):
            raise ValidationError(message = self.message,
                                  code = self.code)


class PersonNumberValidator(BaseValidator):
    """Based on http://www.icosaedro.it/cf-pi/vedi-codice.cgi?f=cf-js.txt
    """

    regex = re.compile(r"^[A-Z0-9]{16}$")
    set_1 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    set_2 = "ABCDEFGHIJABCDEFGHIJKLMNOPQRSTUVWXYZ"
    set_even = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    set_uneven = "BAKPLCQDREVOSFTGUHMINJWZYX"

    def is_valid(self, value):
        value = value.upper()
        if not self.regex.match(value):
            self.message = _(
                u"The code is too short or contains invalid characters"
            )
            return False
        s = 0
        for i in xrange(1, 14, 2):
            s += self.set_even.index(self.set_2[self.set_1.index(value[i])])
        for i in xrange(0, 15, 2):
            s += self.set_uneven.index(self.set_2[self.set_1.index(value[i])])
        if (s % 26) != (ord(value[15]) - ord(u"A")):
            self.message = _(u"The code is malformed")
            return False
        return True


person_number_validator = PersonNumberValidator(
    message = _(u"Invalid person number")
)


class BusinessNumberValidator(BaseValidator):
    """Based on http://www.icosaedro.it/cf-pi/vedi-codice.cgi?f=pi-js.txt
    """

    regex = re.compile(r"^[0-9]{11}$")

    def is_valid(self, value):
        if not self.regex.match(value):
            self.message = _(
                u"The code is too short or contains invalid characters"
            )
            return False
        s = 0
        for i in xrange(0, 10, 2):
            s += ord(value[i]) - ord(u"0")
        for i in xrange(1, 10, 2):
            c = 2 * (ord(value[i]) - ord(u"0"))
            if c > 9:
                c = c - 9
            s += c
        if ((10 - (s % 10)) % 10) != (ord(value[10]) - ord(u"0")):
            self.message = _(u"The code is malformed")
            return False
        return True


business_number_validator = BusinessNumberValidator(
    message = _(u"Invalid Vat number")
)
