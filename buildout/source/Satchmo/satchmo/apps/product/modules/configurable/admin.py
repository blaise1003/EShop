from django.contrib import admin
from product.modules.configurable.models import ConfigurableProduct, ProductVariation

class WriteOnlyModelAdmin(admin.ModelAdmin):
    """On top of ModelAdmin, this class adds one more property:
        writeonly_fields - the readonly_fields named here will
        be like normal readonly fields, except when the model is
        being added. At this instance the fields are editable.
        """
    def add_view(self, *args, **kwargs):
        old_readonly = None
        try:
            self.writeonly_fields # just checking if the name exists.
            try:
                old_readonly = self.readonly_fields
                self.readonly_fields = [
                    f for f in self.readonly_fields
                    if f not in self.writeonly_fields
                    ]
            except AttributeError:
                pass
        except AttributeError:
            pass
        response = super(WriteOnlyModelAdmin, self).add_view(*args, **kwargs)
        if old_readonly:
            self.readonly_fields = old_readonly
        return response

class ProductVariationOptions(WriteOnlyModelAdmin):
    '''
    Makes the fields product and parent read-only.

    Letting the user change the parent on an existing ProductVariation
    will just confuse things, and probably never makes sense.

    If the product_id has been assigned externally (usually by a link
    from said product), then we want it to not be user changeable so it
    doesn't get changed by mistake.
    '''
    readonly_fields = ['product', 'parent',]
    writeonly_fields = ['product', 'parent',]
    fields = ['product', 'parent', 'options',]
    filter_horizontal = ('options',)

class ConfigurableProductAdmin(WriteOnlyModelAdmin):
    '''
    Makes the field product read-only.

    If the product_id has been assigned externally (usually by a link
    from said product), then we want it to not be user changeable so it
    doesn't get changed by mistake.
    '''
    readonly_fields = ['product',]
    writeonly_fields = ['product',]
    fields = ['product', 'create_subs', 'option_group',]

admin.site.register(ConfigurableProduct, ConfigurableProductAdmin)
admin.site.register(ProductVariation, ProductVariationOptions)


