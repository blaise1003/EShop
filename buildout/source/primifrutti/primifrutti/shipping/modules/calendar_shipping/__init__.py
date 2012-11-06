from primifrutti.shipping.modules.calendar_shipping import shipper

def get_methods():
    return [shipper.Shipper()]