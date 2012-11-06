#!/usr/bin/env python
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

log = logging.getLogger('primifrutti.ui.test_views')


@csrf_exempt
def test_confirm_ipn(request):
    """
    test paypal confirm ipn data action.
    return "INVALID" or "VERIFIED".
    See https://www.paypal.com/cgi-bin/webscr?cmd=p/acc/ipn-info-outside
    for specification.
    """
    content = "VERIFIED"
    # content = "INVALID"
    return HttpResponse(content=content)
