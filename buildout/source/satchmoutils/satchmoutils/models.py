from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models.signals import pre_save
from satchmo_store.contact import models as contact_models

from .utils import slugify

# load custom configs
import config # pylint: disable=W0611


class ContactAdministrativeInformation(models.Model):
    contact = models.OneToOneField(
        contact_models.Contact,
        verbose_name = _(u"contact")
    )
    business_number = models.CharField(
        _(u"business number"),
        max_length = 256
    )
    person_number = models.CharField(
        _(u"person number"),
        max_length = 256
    )

    def __unicode__(self):
        # XXX: I have to duplicate here 'ugettext_lazy' import
        # if not '_' is None
        from django.utils.translation import ugettext_lazy as _
        contact_fullname = ''
        if self.contact and self.contact.full_name:
            contact_fullname = self.contact.full_name
        return _(u"administrative information for %(contact_name)s") % {
            'contact_name': contact_fullname}

    class Meta:
        verbose_name = _(u"administrative information")
        verbose_name_plural = _(u"administrative informations")


class Page(models.Model):
    """
    Content definition for Page
    """
    title = models.CharField(
        _(u"Title"),
        max_length=255,
        blank=False,
        null=False)
    slug = models.SlugField(
        _(u"Slug Name"),
        blank=False,
        null=False,
        help_text=_(u"Used for URLs, auto-generated from name if blank"),
        max_length=255)
    text = models.TextField(
        _(u"Text"),
        help_text=_(u"This field can contain HTML"),
        default='',
        blank=True)
    ordering = models.IntegerField(
        _(u"Ordering"),
        default=0,
        help_text=_(u"Override alphabetical order in category display"))
    active = models.BooleanField(
        _(u"Active"),
        default=True,
        help_text=_(u"This will determine whether or not"
                    u" this product will appear on the site"))

    def __unicode__(self):
        return u"%(title)s" % {'title': self.title}

    def get_absolute_url(self):
        return "/pagine/%(slug)s/" % {'slug': self.slug}

    class Meta:
        verbose_name = _("page")
        verbose_name_plural = _("pages")


def slugify_item(sender, **kwargs):
    instance = kwargs['instance']
    if instance.slug in ('', None):
        slug = slugify(instance.title, 47)
        slug_index = 1
        while True:
            try:
                Page.objects.get(slug=slug)
                slug_index += 1
                slug = "%s-%s" % (slug, str(slug_index))
            except Page.DoesNotExist:
                break
        instance.slug = slug


pre_save.connect(slugify_item, sender=Page)


# XXX: we shall load this here so that if anyone tries to import this
# 'models.py', it will find something.
import formextender
formextender.load_extensions()
