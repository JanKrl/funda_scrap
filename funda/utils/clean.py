'''Data cleaning utilities'''
import re

def postcode(address):
    '''Removes a whitespace from postal code into format 1234AB'''
    address_reg = re.match(r'(.*)(\d{4} \D{2})(.*)', address)
    groups = address_reg.groups()
    postal_code = groups[1].replace(' ', '')
    return groups[0] + postal_code + groups[2]

def area(area):
    '''Removes comas, dots and m2 sign'''
    return area.replace(',', '').replace('.', '').rstrip(' m²')

def price(price):
    '''Removes EUR sign and k.k., v.o.n, removes comas'''
    return price.lstrip('€ ').rstrip(' k.k.').rstrip(' v.o.n').replace(',', '')

def rooms(rooms):
    '''Removes rooms text'''
    return rooms.rstrip(' rooms')
