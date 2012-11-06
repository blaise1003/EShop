# -*- coding: utf-8 -*-
from datetime import datetime
import optparse, sys
from livesettings import config_value
from django.template import loader, Context
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _
from satchmo_store.mail import (NoRecipientsException, ShouldNotSendMail,
                                        send_store_mail_template_decorator)
from satchmo_store.shop.signals import ship_notice_sender
from satchmo_store.shop.signals import sending_store_mail

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
    from django.core.mail import send_mail
    
from primifrutti.zones.models import Zone, Shipments

import logging
log = logging.getLogger('zones.mail')


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        optparse.make_option(
            "-d", "--debug",
            action = "count",
            dest = "debug_level",
            default = 0,
            help = ("Shows debug log, multiple uses of the option "
                    "increase the verboseness")
        ),
        optparse.make_option(
            "-l", "--logfile",
            action = "store",
            dest = "logfile",
            default = "",
            metavar = "FILE",
            help = ("logs into FILE. If not given defaults to stderr")
        ),
    )
    help = ("Notify Shop Administrators with stale shipments")

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def setupLogging(self, options):
        kwargs = {
            'level' : 50 - (options['debug_level'] * 10),
            'format': "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        }
        if options.get('logfile', ''):
            kwargs['filename'] = options['logfile']
        else:
            kwargs['stream'] = sys.stderr
        logging.basicConfig(**kwargs)
        if options.get('output', ''):
            return open(options['output'], 'ab')
        else:
            return sys.stdout

    def print_ts(self, message, output):
        output.write("%s @ %s\n" % (
            message,
            datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        ))

    @send_store_mail_template_decorator('zones/email/stale_shipments')
    def send_notification(self, deliveries=[], email='', site_name='',
                        fromemail='', template='', template_html=''):
        c_dict = {
            'site_name': site_name,
            'deliveries': deliveries
        }
        c = Context(c_dict)

        subject = _(u"%(site_name)s - Stale shipments") % {
            'site_name': site_name}

        from_field = "%s" % fromemail
        to_field = email
        
        t = loader.get_template(template)
        message = t.render(c)
        
        # match send_mail's signature
        send_mail_args = {
            'subject': subject,
            'message': message,
            'from_email': from_field,
            'recipient_list': [to_field],
            'fail_silently': False,
        }

        try:
            kwargs = {}
            sending_store_mail.send(ship_notice_sender, send_mail_args=send_mail_args, \
                                    context=c, **kwargs)
        except ShouldNotSendMail:
            return

        if not send_mail_args.get('recipient_list'):
            raise NoRecipientsException

        send_mail(**send_mail_args)


    def handle(self, *args, **options): # pylint: disable=W0613
        """Actually executes the command
        """
        output = self.setupLogging(options)

        self.print_ts("Command started", output)

        max_days = int(config_value('ZONES_INFO', 'MAX_DAYS'))
        zones = Zone.objects.all()
        stale_shipments = []
        for zone in zones:
            shipments = Shipments(zone)
            stale_shipments.extend(
                [x for x in shipments.stale_shipments(max_days)])

        email = settings.EMAIL_NOTIFICATION
        site_name = settings.SITE_NAME
        fromemail = settings.DEFAULT_FROM_EMAIL
        self.send_notification(stale_shipments, email, site_name, fromemail)

        self.print_ts("Command ended", output)
        return 'OK\n'
