# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FundaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    address = scrapy.Field()
    price = scrapy.Field()
    floor_area = scrapy.Field()
    property_area = scrapy.Field()
    rooms = scrapy.Field()
    id = scrapy.Field()
