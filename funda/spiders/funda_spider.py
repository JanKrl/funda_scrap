import csv
import scrapy
import logging
from bs4 import BeautifulSoup

class CitySpider(scrapy.Spider):
    name = "city"
    allowed_domains = ['funda.nl']
    custom_settings = {
        'LOG_LEVEL': logging.INFO
    }

    def __init__(self):
        super().__init__(self)
        self.items = []

    def start_requests(self):
        urls = [
            'http://funda.nl/en/koop/rotterdam/250000-350000/woonhuis/+30km/p1/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.get_items(response.body)
        page = int(response.url.split("/")[-2][1:])

        # Finding next button and opening the page
        next = self.find_next(response.body)

        if next and page < 250: # max 250 pages
            yield scrapy.Request(f'http://{self.allowed_domains[0]}/{next}',\
                callback=self.parse)
        else:
            #self.logger.info("Completed parsing, saving to file")
            self.save_csv()


    def find_next(self, body):
        soup = BeautifulSoup(body, 'html.parser')
        next = soup.find('a', attrs={'rel':'next'})
        return next.get('href') if next else None

    def save_csv(self):
        filename = 'data/rotterdam.csv'
        with open(filename, 'w+') as file:
            writer = csv.DictWriter(file, self.items[0].keys())
            writer.writeheader()
            writer.writerows(self.items)


    def get_items(self, body):
        soup = BeautifulSoup(body, 'html.parser')

        listing = soup.find_all('div', class_='search-result-content-inner')
        for item in listing:
            address_tag = item.find(
                'h2', class_='search-result__header-title fd-m-none')
            address2_tag = item.find('h4', \
                class_='search-result__header-subtitle fd-m-none')

            price_tag = item.find('span',
                              class_='search-result-price')

            floor_area_tag = item.find('span', title='Living area')
            property_area_tag = item.find('span', title='Plot size')

            rooms_tag = item.find('ul', class_='search-result-kenmerken')\
                .find_all('li')[1]

            id_tag = item.find('a', attrs={'data-object-url-tracking': 'resultlist'})

            if address_tag and address2_tag:
                address = address_tag.string.strip() + ' '\
                    + address2_tag.string.strip()
            else:
                address = ''

            price = price_tag.string.strip() if price_tag else ''
            floor_area = floor_area_tag.string.strip() if floor_area_tag else ''
            property_area = property_area_tag.string.strip() if property_area_tag else ''
            rooms = rooms_tag.string.strip() if rooms_tag else ''
            id = id_tag.get('data-search-result-item-anchor') if id_tag else ''

            self.items.append({'address': address,
                          'price': price,
                          'floor_area': floor_area,
                          'property_area': property_area,
                          'rooms': rooms,
                          'id': id})
        return
