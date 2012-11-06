from decimal import Decimal
from l10n.models import Country
from product.models import Product
from satchmo_store.contact.models import Contact, ContactRole, AddressBook
from satchmo_store.shop.models import Order, OrderItem


# pylint: disable=W0102
def make_test_order(site, orderitems, shipping_cost='10.00', contact_info={}):
    default_contact_info = {
        'first_name': "Order",
        'last_name': "Tester",
        'role': ContactRole.objects.get(pk='Customer'),
        'email': "order@example.com",
        'address': {
            'description': 'home',
            'street1': 'Via delle Chiaie 21',
            'city': 'Napoli',
            'state': 'NA',
            'country': Country.objects.get(iso2_code__iexact='IT'),
            'is_default_shipping': True,
            'is_default_billing': True
        }
    }
    default_contact_info.update(contact_info)
    address_info = default_contact_info.pop('address')
    contact = Contact(**default_contact_info)
    contact.save()

    address_info['contact'] = contact
    address_book = AddressBook(**address_info)
    address_book.save()

    order = Order(
        contact=contact,
        shipping_cost=Decimal(shipping_cost),
        site = site
    )
    order.save()

    for slug, quantity in orderitems:
        product = Product.objects.get(slug=slug)
        price = product.unit_price
        item = OrderItem(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=price,
            line_item_price=price*quantity
        )
        item.save()

    return order
