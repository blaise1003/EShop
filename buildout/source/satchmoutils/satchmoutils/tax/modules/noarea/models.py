from django.db import models
from django.utils.translation import ugettext_lazy as _
from product.models import TaxClass

class TaxRate(models.Model):
    """
    Actual percentage tax based on product class
    """
    taxClass = models.ForeignKey(TaxClass, verbose_name=_('tax class'))
    percentage = models.DecimalField(_("Percentage"), max_digits=7,
        decimal_places=6, help_text=_("% tax for this type"))

    def _display_percentage(self):
        return "%#2.2f%%" % (100*self.percentage)
    _display_percentage.short_description = _('Percentage')
    display_percentage = property(_display_percentage)    

    def __unicode__(self):
        return u"%s = %s" % (self.taxClass,
                             self.display_percentage)

    class Meta:
        verbose_name = _("tax rate")
        verbose_name_plural = _("tax rates")
        
import config
