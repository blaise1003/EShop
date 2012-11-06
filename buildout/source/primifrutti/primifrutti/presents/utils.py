# -*- coding: utf-8 -*-
from django import forms
from livesettings import Value
from livesettings.values import NOTSET


class ModelValue(Value):
    """ This Config type gives you possibility to choose one "Model" instance
        as config value.
    """

    def __init__(self, group, key, queryset, **kwargs):
        self.empty_label = kwargs.pop('empty_label', '-----------')
        self.required = kwargs.pop('required', True)
        self.queryset = queryset
        super(ModelValue, self).__init__(group, key, **kwargs)

    @property
    def field(self):

        class field(forms.ModelChoiceField):

            def __init__(inst, **kwargs):
                forms.ModelChoiceField.__init__(
                    inst,
                    queryset=self.queryset,
                    empty_label=self.empty_label,
                    required=self.required,
                    **kwargs)

        return field

    def choice_field(self, **kwargs):
        if self.hidden:
            kwargs['widget'] = forms.MultipleHiddenInput()
        return self.field(**kwargs)

    def to_python(self, value):
        if value == NOTSET:
            return None
        if isinstance(value, unicode) and value.isdigit():
            return self.queryset.get(pk=int(value))
        return value

    def to_editor(self, value):
        if value in (NOTSET, ''):
            return None
        return int(value)

    def get_db_prep_save(self, value):
        if not value:
            return ''
        return unicode(value.pk)

    def _get_choices(self):
        return [(obj.pk, obj) for obj in self.queryset]

    def _set_choices(self, value):
        """ Ignore
        """

    choices = property(_get_choices, _set_choices)
