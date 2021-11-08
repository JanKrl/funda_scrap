import pandas as pd

def clean_area(area_series):
    '''Clears data in columns containing area info
    Fills up blank info with zero
    Removes comas, dots and m²
    Converts to int
    '''
    area_series = area_series.fillna('0 m²')
    area_series = area_series.map(lambda x: x.replace(',', '').replace('.', '').rstrip(' m²'))
    area_series = area_series.astype(int)
    
    return area_series

def clean_price(price_series):
    '''Clears data in columns containing price info
    Converts to int
    '''
    price_series = price_series.map(lambda x: x.lstrip('€ ').rstrip(' k.k.').rstrip(' v.o.n').replace(',', ''))
    price_series = price_series.astype(int)
    
    return price_series

def clean_rooms(rooms_series):
    '''Clears data in columns containing rooms info
    Fills up blank info with zero
    Converts to int
    '''
    rooms_series = rooms_series.fillna('0 rooms')
    rooms_series = rooms_series.map(lambda x: x.rstrip(' rooms'))
    rooms_series = rooms_series.astype(int)
    
    return rooms_series

def remove_postcode_whitespace(address):
    address_df = address.str.extract(r'(.*)(\d{4} \D{2})(.*)')
    address_df[1] = address_df[1].str.replace(' ', '')
    return address_df[0] + address_df[1] + address_df[2]