import os
import logging
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, Context
from django.shortcuts import get_object_or_404
from django.utils.encoding import smart_str
from django.views.decorators.cache import never_cache
from satchmo_store.shop.models import Order
from satchmo_store.shop.models import Config
from livesettings import config_value


def converter(extension):
    def wrapper(func):
        func.dd_extension = extension
        return func
    return wrapper


class DisplayDoc(object):

    def __init__(self):
        self.converter = getattr(settings, 'PDF_RENDERMETHOD', 'rtml2pdf')

    @converter('rml')
    def rtml2pdf(self, data):
        import trml2pdf
        return trml2pdf.parseString(smart_str(data))

    @converter('html')
    def wkhtml2pdf(self, data):
        import subprocess, sys
        executable = settings.WKHTML2PDF_BINARY[sys.platform]
        logger = logging.getLogger('wkhtml2pdf')
        if isinstance(data, unicode):
            data = data.encode("utf-8")
        args = (executable, "-q", "--encoding", "utf-8",
                "--print-media-type", "-", "-")
        process = subprocess.Popen(
            args,
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE
        )
        logger.debug("Calling %s" % " ".join(args))
        stdout, stderr = process.communicate(data)
        if process.returncode != 0:
            logger.error("wkhtmltopdf failed (%d): %s" % (process.returncode,
                                                          stderr))
        return stdout

    def __call__(self, request, id, doc):
        order = get_object_or_404(Order, pk=id)
        shopDetails = Config.objects.get_current()
        filename_prefix = shopDetails.site.domain
        converter_ = getattr(self, self.converter)
        if doc == "invoice":
            filename = "%s-invoice.pdf" % filename_prefix
            template = "invoice." + converter_.dd_extension
        elif doc == "packingslip":
            filename = "%s-packingslip.pdf" % filename_prefix
            template = "packing-slip." + converter_.dd_extension
        elif doc == "shippinglabel":
            filename = "%s-shippinglabel.pdf" % filename_prefix
            template = "shipping-label." + converter_.dd_extension
        else:
            return HttpResponseRedirect('/admin')
        icon_uri = config_value('SHOP', 'LOGO_URI')
        t = loader.get_template(os.path.join('shop/pdf', template))
        c = Context({
            'filename' : filename,
            'iconURI' : icon_uri,
            'shopDetails' : shopDetails,
            'order' : order
        })
        data = converter_(t.render(c))
        response = HttpResponse(mimetype='application/pdf')
        if config_value('SHIPPING','DOWNLOAD_PDFS'):
            response['Content-Disposition'] = 'attachment; filename=%s' % (
                filename,
            )
        response.write(data)
        return response


displayDoc = DisplayDoc()
displayDoc = staff_member_required(never_cache(displayDoc))

