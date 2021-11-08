import requests

def get_coordinates(address):
    url = 'https://nominatim.openstreetmap.org/search'
    params = {'q': address,
              'format': 'json'}
    response = requests.get(url, params).json()
    if response:
        return response[0]['lat'], response[0]['lon']
    return None, None