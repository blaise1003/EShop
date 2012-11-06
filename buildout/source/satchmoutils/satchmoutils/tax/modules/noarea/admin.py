from django.contrib import admin
from django.forms import models
from satchmoutils.tax.modules.noarea.models import TaxRate


class TaxRateForm(models.ModelForm):
    pass
    
    
class TaxRateOptions(admin.ModelAdmin):
    list_display = ("taxClass", "display_percentage")
    form = TaxRateForm
    
    
admin.site.register(TaxRate, TaxRateOptions)
