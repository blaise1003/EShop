# -*- coding: utf-8 -*-
import re
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.utils.translation import ungettext, ugettext_lazy as _
from django.utils.functional import update_wrapper
from django.utils.safestring import mark_safe
from django.forms import HiddenInput
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.util import unquote
from .models import (Zone, Calendar, CalendarDay, Mission, ContactZone,
                     WEEK_DAYS)


def expunge(obj, iterable):
    data = []
    for element in iterable:
        if isinstance(element, iterable.__class__):
            children = expunge(obj, element)
            if len(children) > 0:
                data.append(children)
        elif element != obj:
            data.append(element)
    return iterable.__class__(data)


def contained_view(view):
    def wrapper(self, request, *args, **kwargs):
        self.set_container(request, kwargs)
        return view(self, request, *args, **kwargs)
    return update_wrapper(wrapper, view)


class ContainedAdmin(admin.ModelAdmin):

    container_link = ''

    def __init__(self, model, admin_site, container_admin):
        super(ContainedAdmin, self).__init__(model, admin_site)
        self.container_admin = container_admin
        self.container_object = None

    def set_container(self, request, kwargs):
        self.container_object = self.container_admin.get_object(
            request,
            unquote(kwargs.pop('parent'))
        )

    def queryset(self, request):
        queryset = super(ContainedAdmin, self).queryset(request)
        return queryset.filter(**{self.container_link: self.container_object})

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(ContainedAdmin, self).formfield_for_dbfield(
            db_field,
            **kwargs
        )
        if db_field.name == self.container_link:
            field.widget = HiddenInput()
        return field

    def get_form(self, request, obj=None, **kwargs):
        # Obtain the class declaration from above
        ModelForm = super(ContainedAdmin, self).get_form(
            request,
            obj=obj,
            **kwargs
        )

        f_name = self.container_link
        f_value = self.container_object

        old__init = ModelForm.__init__
        # This is the overridden __init__, also incidentally a closure
        def new__init(inst, *args, **kwargs):
            kwargs.setdefault('initial', {})[f_name] = f_value
            old__init(inst, *args, **kwargs)

        ModelForm.__init__ = new__init
        return ModelForm

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(ContainedAdmin, self).get_fieldsets(
            request,
            obj=obj
        )
        for __, fieldset in fieldsets:
            fieldset['fields'] = expunge(
                self.container_link,
                fieldset['fields']
            )
        fieldsets.append((
            'Parent',
            {
                'fields': (self.container_link,),
                'classes': ('empty-form',)
            }
        ))
        return fieldsets

    def save_model(self, request, obj, form, change):
        setattr(obj, self.container_link, self.container_object)
        return super(ContainedAdmin, self).save_model(
            request,
            obj,
            form,
            change
        )

    def info(self):
        # pylint: disable=W0212
        return [
            self.model._meta.app_label,
            self.model.__name__.lower()
        ]

    changelist_view = contained_view(admin.ModelAdmin.changelist_view)
    add_view = contained_view(admin.ModelAdmin.add_view)
    history_view = contained_view(admin.ModelAdmin.history_view)
    delete_view = contained_view(admin.ModelAdmin.delete_view)
    change_view = contained_view(admin.ModelAdmin.change_view)


class ContainerAdmin(admin.ModelAdmin):

    contained = []

    def __init__(self, model, admin_site):
        super(ContainerAdmin, self).__init__(model, admin_site)
        self.contained_admins = []
        for model, admin_class in self.contained:
            self.contained_admins.append(
                admin_class(model, self.admin_site, self)
            )

    def get_urls(self):
        from django.conf.urls.defaults import patterns, include

        urls = []
        for contained_admin in self.contained_admins:
            urls.append(
                patterns(
                    '',
                    (
                        r'^(?P<parent>\d+)/%s/%s/' % tuple(
                            re.escape(i) for i in contained_admin.info()
                        ),
                        include(contained_admin.get_urls())
                    )
                )
            )
        urls.append(super(ContainerAdmin, self).get_urls())
        return reduce(lambda x, y: x+y, urls[1:], urls[0])


class DayInline(admin.TabularInline):
    model = Mission
    weekday = 0
    extra = 1

    def __init__(self, parent_model, admin_site): # pylint: disable=W0613
        super(DayInline, self).__init__(
            CalendarDay,
            admin_site
        )

    def get_weekday_for(self, obj):
        try:
            return obj.calendarday_set.all().get(weekday=self.weekday)
        except CalendarDay.DoesNotExist:
            return CalendarDay.objects.create(
                calendar=obj,
                weekday=self.weekday
            )

    def get_formset(self, request, obj=None, **kwargs):
        if obj is not None:
            obj = self.get_weekday_for(obj)
        FormSet = super(DayInline, self).get_formset(
            request,
            obj=obj,
            **kwargs
        )
        old__init = FormSet.__init__
        def new__init(inst, *args, **kwargs):
            if 'instance' in kwargs:
                kwargs['instance'] = self.get_weekday_for(kwargs['instance'])
            old__init(inst, *args, **kwargs)
        FormSet.__init__ = new__init
        return FormSet


class CalendarAdmin(ContainedAdmin):
    inlines = [
        type(
            'Day%dInline' % w[0],
            (DayInline,),
            {
                'weekday': w[0],
                'verbose_name': _(u"%(day)s's mission") % { 'day': w[1] },
                'verbose_name_plural': _(u"%(day)s's missions") % {
                    'day': w[1]
                }
            }
        ) for w  in WEEK_DAYS
    ]

    @contained_view
    def add_view(self, request, form_url='', extra_context=None):
        inline_instances = [ i for i in self.inline_instances ]
        self.inline_instances = []
        response = admin.ModelAdmin.add_view(
            self,
            request,
            form_url=form_url,
            extra_context=extra_context
        )
        self.inline_instances = inline_instances
        return response


class ExceptionalCalendarAdmin(CalendarAdmin):

    container_link = 'zone'
    list_display = ('id', 'valid_from', 'valid_to', 'slack_days')
    date_hierarchy = 'valid_from'

    def info(self):
        info = super(ExceptionalCalendarAdmin, self).info()
        info[1] = 'exceptional-calendars'
        return info

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(ExceptionalCalendarAdmin, self).formfield_for_dbfield(
            db_field,
            **kwargs
        )
        if db_field.name in ['valid_from', 'valid_to']:
            field.required = True
        return field

    def queryset(self, request):
        query = super(ExceptionalCalendarAdmin, self).queryset(request)
        return query.filter(
            valid_from__isnull=False,
            valid_to__isnull=False
        )


class DefaultCalendarAdmin(CalendarAdmin):

    container_link = 'zone'
    exclude = ('valid_from', 'valid_to')
    add_form_template = 'admin/zones/calendar/default_change_form.html'
    change_form_template = 'admin/zones/calendar/default_change_form.html'
    object_history_template = 'admin/zones/calendar/default_object_history.html'

    def queryset(self, request):
        query = super(DefaultCalendarAdmin, self).queryset(request)
        return query.filter(
            valid_from__isnull=True,
            valid_to__isnull=True
        )

    def info(self):
        info = super(DefaultCalendarAdmin, self).info()
        info[1] = 'default-calendar'
        return info

    def response_change(self, request, obj):
        super(DefaultCalendarAdmin, self).response_change(
            request,
            obj
        )
        if "_continue" in request.POST:
            if "_popup" in request.REQUEST:
                return HttpResponseRedirect(request.path + "?_popup=1")
            else:
                return HttpResponseRedirect(request.path)
        return HttpResponseRedirect('../../../')

    def response_add(self, request, obj, post_url_continue='../%s/'):
        super(DefaultCalendarAdmin, self).response_add(
            request,
            obj,
            post_url_continue=post_url_continue
        )
        if "_continue" in request.POST:
            if "_popup" in request.POST:
                post_url_continue += "?_popup=1"
            return HttpResponseRedirect(post_url_continue % obj.pk)
        return HttpResponseRedirect('../../../')

    def has_add_permission(self, request):
        add_permission = super(DefaultCalendarAdmin, self).has_add_permission(
            request
        )
        if request.path_info.endswith('/add/'):
            return add_permission
        return False

    def has_delete_permission(self, request, obj=None): # pylint: disable=W0613
        return False

    def get_urls(self):
        urls = []
        default_urls = super(DefaultCalendarAdmin, self).get_urls()
        for url in default_urls:
            if url.name.endswith('_history') or \
                    url.name.endswith('_change') or url.name.endswith('_add'):
                url.name += '_default'
                urls.append(url)
        return urls


class ZoneAdmin(ContainerAdmin):
    exclude = ('active',)
    search_fields = ['^name']
    actions = ['activate', 'deactivate']
    list_display = ('name', 'active')
    list_display_links = ('name',)
    list_filter = ('active',)

    contained = [
        (Calendar, ExceptionalCalendarAdmin),
        (Calendar, DefaultCalendarAdmin)
    ]

    def _toggle_zone(self, queryset, activate):
        n_done = 0
        n_failed = 0
        errors = []
        messages_ = []
        for zone in queryset:
            try:
                if activate:
                    zone.activate()
                else:
                    zone.deactivate()
            except ValidationError, e:
                errors.append((
                    zone,
                    e
                ))
                n_failed += 1
            else:
                n_done += 1
        if n_done > 0:
            messages_.append((
                'info',
                ungettext(
                    u'%(count)d zone activated',
                    u'%(count)d zones activated',
                    n_done
                ) % { 'count': n_done }
            ))
        if n_failed > 0:
            template = u'%s. %s'
            summary = ungettext(
                u"%(count)d zone couldn't be activated",
                u"%(count)d zones couldn't be activated",
                n_failed
            ) % { 'count': n_failed }
            details = []
            for zone, exception in errors:
                details.append(u', '.join(exception.messages))
            messages_.append((
                'error',
                mark_safe(
                    template % (
                        summary,
                        u'; '.join(details)
                    )
                )
            ))
        return messages_

    def activate(self, request, queryset):
        for level, message in self._toggle_zone(queryset, activate=True):
            getattr(messages, level)(request, message)
    activate.short_description = _("Activate zones")

    def deactivate(self, request, queryset):
        for level, message in self._toggle_zone(queryset, activate=False):
            getattr(messages, level)(request, message)
    deactivate.short_description = _("Deactivate zones")

    def save_model(self, request, obj, form, change):
        if not change:
            messages.warning(
                request,
                _(u"Before you can activate this zone, you must create a "
                  u"default calendar and populate it")
            )
        super(ZoneAdmin, self).save_model(request, obj, form, change)



admin.site.register(Zone, ZoneAdmin)
admin.site.register(ContactZone)

