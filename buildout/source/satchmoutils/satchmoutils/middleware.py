from django.conf import settings
from django.utils.translation import check_for_language

import logging

logger = logging.getLogger("MIDDLEWARE LOG")


class ContentLengthWriter(object):
    """A simple middleware that writes content-length
    """

    def process_response(self, request, response):
        if not response.has_header('Content-Length'):
            response['Content-Length'] = str(len(response.content))
        return response
