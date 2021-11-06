import scrapy
import logging
from scrapy.utils.log import configure_logging
from funda.items import FundaItem
from bs4 import BeautifulSoup

class FundaSpider(scrapy.Spider):
    name = "funda"
    allowed_domains = ['funda.nl']

    def __init__(self, search_criteria, *args, **kwargs):
        super().__init__(*args, **kwargs)
        configure_logging({'LOG_LEVEL': logging.INFO})

        self.search_criteria = search_criteria



    def start_requests(self):
        url = ['http://funda.nl/en/koop/']
        criteria = '/'.join(self.search_criteria)
        urls = [
            f'http://funda.nl/en/koop/{criteria}/p1/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        items = self.get_items(response.body)
        for item in items:
            yield item

        # Finding next button and opening the page
        next = self.find_next(response.body)
        next_url = f'http://{self.allowed_domains[0]}/{next}'

        # Find link to the next page and yield the request
        page = int(response.url.split("/")[-2][1:])
        if next and page < 5: # max 5 pages
            yield response.follow(next_url, callback=self.parse)


    def find_next(self, body):
        soup = BeautifulSoup(body, 'html.parser')
        next = soup.find('a', attrs={'rel':'next'})
        return next.get('href') if next else None

    def get_items(self, body):
        soup = BeautifulSoup(body, 'html.parser')
        items = []

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

            items.append(FundaItem(address=address,
                            price=price,
                            floor_area=floor_area,
                            property_area=property_area,
                            rooms=rooms,
                            id=id,
                            search_area=self.search_criteria[0]))
        return items
