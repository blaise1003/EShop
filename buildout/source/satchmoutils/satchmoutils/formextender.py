try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module
from types import MethodType
from collections import Sequence
from django.conf import settings
from signals_ahoy.signals import form_init, form_postsave


class ExtraField(object):

    def __init__(self, klass, name, css_class='', **kwargs):
        self.name = name
        self.klass = klass
        self.css_class = css_class
        self.kwargs = kwargs

    def __call__(self):
        field = self.klass(**self.kwargs)
        field.widget.attrs['class'] = self.css_class
        return field


class Fieldset(object):

    def __init__(self, id_, label, fields, before=None):
        self.id_ = id_
        self.label = label
        self.fields = fields
        self.before = before
        self.form = None
        self._reorder()

    def _reorder(self):
        new_fields = []
        for field in self.fields:
            if isinstance(field, tuple):
                try:
                    index = self.fields.index(field[1])
                except ValueError:
                    new_fields.append(field[0])
                else:
                    new_fields.insert(index, field[0])
            else:
                new_fields.append(field)
        self.fields = new_fields

    def bind(self, form):
        copy = self.__class__(self.id_, self.label, self.fields,
                              before=self.before)
        copy.form = form
        return copy

    def merge(self, other):
        self.label = other.label
        self.fields.extend(other.fields)
        if other.before:
            self.before = other.before
        self._reorder()

    def items(self):
        for field_name in self.fields:
            bound_field = self.form[field_name]
            css_class = bound_field.field.widget.attrs.get('class', '')
            yield (field_name, css_class, bound_field)


class Fieldsets(Sequence):

    def __init__(self, initial = tuple()):
        self.elements = list(initial)
        self.ids = {}
        for element in self.elements:
            self.ids[element.id_] = element

    def __len__(self):
        return len(self.elements)

    def __iter__(self):
        return iter(self.elements)

    def __contains__(self, item):
        return item.id_ in self.ids

    def __getitem__(self, index):
        return self.elements[index]

    def _reorder(self):
        for index, element in enumerate([ e for e in self.elements ]):
            if element.before is not None:
                try:
                    new_index = self.elements.index(self.ids[element.before])
                except (KeyError, ValueError):
                    pass
                else:
                    del self.elements[index]
                    self.elements.insert(new_index, element)

    def add(self, item):
        if item.id_ in self.ids:
            fieldset = self.ids[item.id_]
            fieldset.merge(item)
        else:
            self.ids[item.id_] = item
            self.elements.append(item)
        self._reorder()

    def update(self, items):
        for item in items:
            self.add(item)


class Extender(object):
    """Usage::

        >>> class MyExtender(Extender):
        ...     extends = (MyForm,)
        ...     fields = [
        ...         ExtraField(CharField, name='foo')
        ...     ]
        ...     fieldsets = [
        ...         Fieldset('test', _(u"Test"), 'foo')
        ...     ]
        ...     @classmethod
        ...     def handle_initdata(cls, **kwargs):
        ...         pass
        ...     @classmethod
        ...     def handle_postsave(cls, **kwargs):
        ...         pass

    Then add into ``settings.py``::

        SATCHMO_SETTINGS = {
           ...
           'FORM_EXTENDERS': [
               'dotted.name.of.module:MyExtender'
           ]
        }
    """

    fields = []
    methods = {}

    @classmethod
    def get_extends(cls):
        if hasattr(cls, 'extends'):
            return cls.extends
        return tuple()

    @classmethod
    def get_fields(cls):
        return cls.fields

    @classmethod
    def get_methods(cls):
        return cls.methods

    @classmethod
    def get_fieldsets(cls):
        if hasattr(cls, 'fieldsets'):
            return cls.fieldsets
        return []

    @classmethod
    def handle_init(cls, **kwargs):
        form = kwargs['form']
        for extrafield in cls.get_fields():
            form.fields[extrafield.name] = extrafield()
        for name, method in cls.get_methods().items():
            form.__dict__[name] = MethodType(method, form,
                                             form.__class__)
        if len(cls.get_fieldsets()) > 0:
            if not hasattr(form, 'fieldsets'):
                form.fieldsets = Fieldsets()
            form.fieldsets.update([f.bind(form) for f in cls.get_fieldsets()])

    @classmethod
    def extend(cls):
        for form_class in cls.get_extends():
            form_init.connect(cls.handle_init, sender=form_class)
            if hasattr(cls, 'handle_initdata'):
                form_init.connect(cls.handle_initdata, sender=form_class)
            if hasattr(cls, 'handle_postsave'):
                form_postsave.connect(cls.handle_postsave, sender=form_class)


def import_path(path):
    module, name = path.split(':')
    module = import_module(module)
    return getattr(module, name)


def load_extensions():
    """Reads the setting ``SATCHMO_SETTINGS['FORM_EXTENDERS']``, which is a
    list of extenders in the form ``dotted.name.of.module:Class``, and loads
    them
    """
    satchmo_settings = getattr(settings, 'SATCHMO_SETTINGS', {})
    extenders = [
        import_path(p) for p in satchmo_settings.get('FORM_EXTENDERS', [])
    ]
    for extender in extenders:
        extender.extend()
