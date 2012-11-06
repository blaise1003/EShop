import optparse, sys, logging, httplib, urllib
from django.conf import settings
from datetime import datetime
from django.core.management.base import BaseCommand
from satchmo_store.shop.models import Order


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
        optparse.make_option(
            "-o", "--order-id",
            action = "store",
            dest = "order_id",
            metavar = "ORDER_ID",
            help = ("ID of a existing order")
        ),
    )
    help = ("Simulate PayPal IPN process for given order.\n"
            "You must set the PayPal Test POST URL to "
            "'http://localhost:8000/test_confirm_ipn/' in '/settings'.")

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

    def handle(self, *args, **options): # pylint: disable=W0613
        """Actually executes the command
        """
        output = self.setupLogging(options)

        self.print_ts("Testing started", output)

        try:
            order = Order.objects.get(id=int(options['order_id']))
        except (KeyError, ValueError, Order.DoesNotExist) as e:
            if isinstance(e, KeyError):
                output.write(
                    "You must pass the order id via the '--order-id' option"
                )
            else:
                output.write(
                    "Order '%s' does not exist.\n" % options['order_id']
                )
            self.print_ts("Testing ended", output)
            return False

        # Check if order is payed thru PayPal
        # XXX: It should be a good thing if PayPal payment processor's
        # "ipn" view makes same control onto given order
        payments = order.payments.all().order_by('id')
        if payments and (payments[0].payment == u"PAYPAL"):
            first_payment = payments[0]
            txn_id = first_payment.transaction_id
        else:
            output.write(
                "Order '%s' isn't paid through PayPal\n" % options['order_id']
            )
            self.print_ts("Testing ended", output)
            return False
        site_domain = settings.SITE_DOMAIN
        url = '/checkout/paypal/ipn/'
        params = urllib.urlencode({
            'payment_status': 'Completed',
            'invoice': order.id,
            'mc_gross': order.total,
            'txn_id': txn_id
        })
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain"
        }
        conn = httplib.HTTPConnection(site_domain, 8000)
        conn.request('POST', url, params, headers)
        response = conn.getresponse()
        output.write(
            "The view replied with a: %s %s\n" % (
                response.status,
                response.reason
            )
        )
        conn.close()
        self.print_ts("Testing ended", output)
        return 'OK\n'
