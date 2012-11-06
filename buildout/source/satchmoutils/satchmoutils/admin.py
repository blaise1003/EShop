from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from tinymce.widgets import TinyMCE
from .models import ContactAdministrativeInformation, Page


class ContactAdministrativeInformationOptions(admin.ModelAdmin):
    __name__ = "ContactAdministrativeInformation Options"

    search_fields = ['contact__first_name', 'contact__last_name']


class PageOptions(admin.ModelAdmin):
    __name__ = "Static Page Options"

    search_fields = ['title']
    actions = ('make_active', 'make_not_active')
    prepopulated_fields = {"slug": ("title",)}
    list_display = ()

    list_display += ('title', 'ordering', 'active')
    list_display_links = ('title',)

    def make_active(self, request, queryset):
        queryset.update(active=True)
        self.message_user(request, _(u"Page updtated"))
        return HttpResponseRedirect('')
    make_active.short_description = _(u"activate")

    def make_not_active(self, request, queryset):
        queryset.update(active=False)
        self.message_user(request, _(u"Page updtated"))
        return HttpResponseRedirect('')
    make_not_active.short_description = _(u"deactivate")

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ('text', 'text_mobile'):
            return db_field.formfield(widget=TinyMCE(
                attrs={'cols': 80, 'rows': 30},
            ))
        return super(PageOptions, self).formfield_for_dbfield(
            db_field, **kwargs)

    class Media:
        js = [
            '/static/theme/scripts/tiny_mce/tiny_mce.js',
            '/static/theme/scripts/tiny_mce/textareas.js']


admin.site.register(
    ContactAdministrativeInformation,
    ContactAdministrativeInformationOptions)
admin.site.register(
    Page,
    PageOptions)
