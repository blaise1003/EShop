from django import forms
from django import template
from django.contrib import admin
from django.conf import settings
from django.utils.translation import (ugettext, ungettext_lazy, ungettext,
                                                ugettext_lazy as _)
from django.http import HttpResponseRedirect
from django.core.files.images import get_image_dimensions
from django.contrib.admin import helpers
from django.utils.safestring import mark_safe

from django.forms.widgets import flatatt
try:
    from django.utils.encoding import smart_unicode
except ImportError:
    from django.forms.util import smart_unicode
from django.utils.html import escape
from django.utils import simplejson

from django.contrib.admin.options import csrf_protect_m, IncorrectLookupParameters
from django.core.exceptions import PermissionDenied
from django.shortcuts import render_to_response
from django.utils.encoding import force_unicode

from ajax_select.fields import AutoCompleteSelectField
from product.admin import ProductOptions
from product.models import Product
from satchmo_store.shop.admin import OrderOptions
from satchmo_store.shop.models import Order
from satchmo_utils.numbers import round_decimal

from tinymce.widgets import TinyMCE
from tinymce.widgets import get_language_config
import tinymce.settings

from .models import Offer, Banner, ProductFeaturedSorting
import config # pylint: disable=W0611


def banner_help_text():

    return ugettext(u"the image to show on the banner. It should be "
                    u"<strong>exactly %(width)s pixel wide and "
                    u"%(height)s pixel high</strong>.") % {
        'height': getattr(settings, 'MAX_WIDTH', 630),
        'width': getattr(settings, 'MAX_HEIGHT', 255)}


class PictureForm(forms.ModelForm):

    def clean_picture(self):
        picture = self.cleaned_data.get("picture")
        if not picture:
            raise forms.ValidationError(_(u"No image!"))
        else:
            max_w = getattr(settings, 'MAX_WIDTH', 630)
            max_h = getattr(settings, 'MAX_HEIGHT', 255)
            w, h = get_image_dimensions(picture)
            sizes = [(w, max_w, _(u'wide')), (h, max_h, _(u'high'))]
            for size, max_size, size_label in sizes:
                if size != max_size:
                    raise forms.ValidationError(
                        _(u"The image is %(current)i pixel %(measure)s. "
                          u"It's supposed to be %(max)i pixel %(measure)s") % {
                            'current': w,
                            'measure': size_label,
                            'max': max_w})
        return picture


class PictureAdmin(admin.ModelAdmin):

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ('picture',):
            return db_field.formfield(help_text=banner_help_text())
        return super(PictureAdmin, self).formfield_for_dbfield(
                                                        db_field, **kwargs)


class OfferForm(PictureForm):

    product = AutoCompleteSelectField('product', required=True)

    class Meta:
        model = Offer


class OfferOptions(PictureAdmin):

    __name__ = _(u"Offer Options")
    form = OfferForm
    list_display = ()

    list_display += ('product', 'active')
    search_fields = ['product__name']
    actions = ('make_active', 'make_not_active')

    def make_active(self, request, queryset):
        n_done = queryset.update(active=True)
        message = ungettext_lazy(
            u'%(count)d offer activated',
            u'%(count)d offers activated',
            n_done) % {'count': n_done}
        self.message_user(request, message)
        return HttpResponseRedirect('')
    make_active.short_description = _(u"Activate")

    def make_not_active(self, request, queryset):
        n_done = queryset.update(active=False)
        message = ungettext_lazy(
            u'%(count)d offer deactivated',
            u'%(count)d offers deactivated',
            n_done) % {'count': n_done}
        self.message_user(request, message)
        return HttpResponseRedirect('')
    make_not_active.short_description = _(u"Deactivate")

    class Media:
        css = {
            'all': ('/static/css/jquery.autocomplete.css',)}

        js = [
            '/static/theme/scripts/jquery.autocomplete.js',
            '/static/theme/scripts/ajax_select.js']


class BannerForm(PictureForm):

    class Meta:
        model = Banner


class BannerOptions(PictureAdmin):

    form = BannerForm
    inlines = []
    actions = ('make_active', 'make_not_active')
    list_display = ()

    list_display += ('title', 'url', 'active')
    search_fields = ['title']

    def make_active(self, request, queryset):
        n_done = queryset.update(active=True)
        message = ungettext_lazy(
            u'%(count)d banner activated',
            u'%(count)d banners activated',
            n_done) % {'count': n_done}
        self.message_user(request, message)
        return HttpResponseRedirect('')
    make_active.short_description = _(u"Activate")

    def make_not_active(self, request, queryset):
        n_done = queryset.update(active=False)
        message = ungettext_lazy(
            u'%(count)d banner deactivated',
            u'%(count)d banners deactivated',
            n_done) % {'count': n_done}
        self.message_user(request, message)
        return HttpResponseRedirect('')
    make_not_active.short_description = _(u"Deactivate")


class ProductSorting_Inline(admin.TabularInline):
    model = ProductFeaturedSorting
    extra = 1


class ProductTinyMCE(TinyMCE):
    """Override TinyMCE widget in order to remove image 
    plugin from default config from settings"""

    def remove_plugin(self, mce_config, plugin):
        """Remove plugin from default MCE configuration"""
        for line in ['1', '2', '3']:
            line_buttons = "theme_advanced_buttons%s" % line
            line_config = mce_config[line_buttons]
            line_config = line_config.replace('%s,' % plugin, '')
            line_config = line_config.lstrip('|,')
            mce_config[line_buttons] = line_config
        return mce_config

    def render(self, name, value, attrs=None):
        if value is None: value = ''
        value = smart_unicode(value)
        final_attrs = self.build_attrs(attrs)
        final_attrs['name'] = name
        assert 'id' in final_attrs, "TinyMCE widget attributes must contain 'id'"

        mce_config = tinymce.settings.DEFAULT_CONFIG.copy()

        # remove image plugin
        mce_config = self.remove_plugin(mce_config, 'image')

        mce_config.update(get_language_config(self.content_language))
        if tinymce.settings.USE_FILEBROWSER:
            mce_config['file_browser_callback'] = "djangoFileBrowser"
        mce_config.update(self.mce_attrs)
        if not 'mode' in mce_config:
            mce_config['mode'] = 'exact'
        if mce_config['mode'] == 'exact':
            mce_config['elements'] = final_attrs['id']
        mce_config['strict_loading_mode'] = 1
        
        # Fix for js functions
        js_functions = {}
        for k in ('paste_preprocess','paste_postprocess'):
            if k in mce_config:
               js_functions[k] = mce_config[k]
               del mce_config[k]
        mce_json = simplejson.dumps(mce_config)
        for k in js_functions:
            index = mce_json.rfind('}')
            mce_json = mce_json[:index]+', '+k+':'+js_functions[k].strip()+mce_json[index:]
            
        html = [u'<textarea%s>%s</textarea>' % (flatatt(final_attrs), escape(value))]
        if tinymce.settings.USE_COMPRESSOR:
            compressor_config = {
                'plugins': mce_config.get('plugins', ''),
                'themes': mce_config.get('theme', 'advanced'),
                'languages': mce_config.get('language', ''),
                'diskcache': True,
                'debug': False,
            }
            compressor_json = simplejson.dumps(compressor_config)
            html.append(u'<script type="text/javascript">tinyMCE_GZ.init(%s)</script>' % compressor_json)
        html.append(u'<script type="text/javascript">tinyMCE.init(%s)</script>' % mce_json)

        return mark_safe(u'\n'.join(html))


class PrimiFruttiProductOptions(ProductOptions):
    inlines = [ProductSorting_Inline,] + ProductOptions.inlines
    list_display = ProductOptions.list_display + ('home_ordering',)
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ('description',):
            return db_field.formfield(widget=ProductTinyMCE(
                attrs={'cols': 80, 'rows': 30},
            ))
        return super(PrimiFruttiProductOptions, self).formfield_for_dbfield(
                                                            db_field, **kwargs)

    def home_ordering(self, obj):
        productfeaturedsorting_set = obj.productfeaturedsorting_set.all()
        if productfeaturedsorting_set:
            return productfeaturedsorting_set[0].ordering
        return 0
    home_ordering.short_description = _(u'Home order')

    class Media:
        js = [
            '/static/theme/scripts/tiny_mce/tiny_mce.js',
            '/static/theme/scripts/tiny_mce/textareas.js',
        ]


class PrimiFruttiOrderOptions(OrderOptions):
    """Override for custom changelist_view"""
    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        "The 'change list' admin view for this model."
        from django.contrib.admin.views.main import ERROR_FLAG
        opts = self.model._meta
        app_label = opts.app_label
        if not self.has_change_permission(request, None):
            raise PermissionDenied

        # Check actions to see if any are available on this changelist
        actions = self.get_actions(request)

        # Remove action checkboxes if there aren't any actions available.
        list_display = list(self.list_display)
        if not actions:
            try:
                list_display.remove('action_checkbox')
            except ValueError:
                pass

        ChangeList = self.get_changelist(request)
        try:
            cl = ChangeList(request, self.model, list_display, self.list_display_links,
                self.list_filter, self.date_hierarchy, self.search_fields,
                self.list_select_related, self.list_per_page, self.list_editable, self)
        except IncorrectLookupParameters:
            # Wacky lookup parameters were given, so redirect to the main
            # changelist page, without parameters, and pass an 'invalid=1'
            # parameter via the query string. If wacky parameters were given
            # and the 'invalid=1' parameter was already in the query string,
            # something is screwed up with the database, so display an error
            # page.
            if ERROR_FLAG in request.GET.keys():
                return render_to_response('admin/invalid_setup.html', {'title': _('Database error')})
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')

        # If the request was POSTed, this might be a bulk action or a bulk
        # edit. Try to look up an action or confirmation first, but if this
        # isn't an action the POST will fall through to the bulk edit check,
        # below.
        action_failed = False
        selected = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)

        # Actions with no confirmation
        if (actions and request.method == 'POST' and
                'index' in request.POST and '_save' not in request.POST):
            if selected:
                response = self.response_action(request, queryset=cl.get_query_set())
                if response:
                    return response
                else:
                    action_failed = True
            else:
                msg = _("Items must be selected in order to perform "
                        "actions on them. No items have been changed.")
                self.message_user(request, msg)
                action_failed = True

        # Actions with confirmation
        if (actions and request.method == 'POST' and
                helpers.ACTION_CHECKBOX_NAME in request.POST and
                'index' not in request.POST and '_save' not in request.POST):
            if selected:
                response = self.response_action(request, queryset=cl.get_query_set())
                if response:
                    return response
                else:
                    action_failed = True

        # If we're allowing changelist editing, we need to construct a formset
        # for the changelist given all the fields to be edited. Then we'll
        # use the formset to validate/process POSTed data.
        formset = cl.formset = None

        # Handle POSTed bulk-edit data.
        if (request.method == "POST" and cl.list_editable and
                '_save' in request.POST and not action_failed):
            FormSet = self.get_changelist_formset(request)
            formset = cl.formset = FormSet(request.POST, request.FILES, queryset=cl.result_list)
            if formset.is_valid():
                changecount = 0
                for form in formset.forms:
                    if form.has_changed():
                        obj = self.save_form(request, form, change=True)
                        self.save_model(request, obj, form, change=True)
                        form.save_m2m()
                        change_msg = self.construct_change_message(request, form, None)
                        self.log_change(request, obj, change_msg)
                        changecount += 1

                if changecount:
                    if changecount == 1:
                        name = force_unicode(opts.verbose_name)
                    else:
                        name = force_unicode(opts.verbose_name_plural)
                    msg = ungettext("%(count)s %(name)s was changed successfully.",
                                    "%(count)s %(name)s were changed successfully.",
                                    changecount) % {'count': changecount,
                                                    'name': name,
                                                    'obj': force_unicode(obj)}
                    self.message_user(request, msg)

                return HttpResponseRedirect(request.get_full_path())

        # Handle GET -- construct a formset for display.
        elif cl.list_editable:
            FormSet = self.get_changelist_formset(request)
            formset = cl.formset = FormSet(queryset=cl.result_list)

        # Build the list of media to be used by the formset.
        if formset:
            media = self.media + formset.media
        else:
            media = self.media

        # Build the action form and populate it with available actions.
        if actions:
            action_form = self.action_form(auto_id=None)
            action_form.fields['action'].choices = self.get_action_choices(request)
        else:
            action_form = None

        selection_note_all = ungettext('%(total_count)s selected',
            'All %(total_count)s selected', cl.result_count)

        # Calculate total
        orders_total = 0
        for order in cl.result_list:
            orders_total += order.total
            
        context = {
            'module_name': force_unicode(opts.verbose_name_plural),
            'selection_note': _('0 of %(cnt)s selected') % {'cnt': len(cl.result_list)},
            'selection_note_all': selection_note_all % {'total_count': cl.result_count},
            'title': cl.title,
            'is_popup': cl.is_popup,
            'cl': cl,
            'media': media,
            'has_add_permission': self.has_add_permission(request),
            'root_path': self.admin_site.root_path,
            'app_label': app_label,
            'action_form': action_form,
            'actions_on_top': self.actions_on_top,
            'actions_on_bottom': self.actions_on_bottom,
            'actions_selection_counter': self.actions_selection_counter,
            'orders_total': round_decimal(val=orders_total, places=2, roundfactor='0.001', normalize=True)
        }
        context.update(extra_context or {})
        context_instance = template.RequestContext(request, current_app=self.admin_site.name)
        return render_to_response('admin/orders/change_list.html', context, context_instance=context_instance)


admin.site.register(Offer, OfferOptions)
admin.site.register(Banner, BannerOptions)
admin.site.unregister(Product)
admin.site.register(Product, PrimiFruttiProductOptions)
admin.site.unregister(Order)
admin.site.register(Order, PrimiFruttiOrderOptions)
