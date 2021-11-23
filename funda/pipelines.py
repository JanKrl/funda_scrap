# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
import csv
import requests
import logging
from funda.utils import clean
from datetime import date
from scrapy.exporters import CsvItemExporter
from scrapy.exceptions import CloseSpider

class SaveToFilePipeline:
    def open_spider(self, spider):
        self.exporter_files = {}
        self.items_processed = 0
        self.items_already_exist = 0
        self.previous_records = {}


    def close_spider(self, spider):
        logging.log(logging.INFO, f'Items processed {self.items_processed}')
        logging.log(logging.INFO, f'Items existed {self.items_already_exist}')

        # Check for previous records not found this time
        items_removed = 0
        with open(f'data/{spider.search_area}-{date.today()}_removed.csv', 'w+') as csvfile:
            writer = csv.writer(csvfile)
            for key, value in self.previous_records.items():
                if value:
                    items_removed += 1
                    writer.writerow([key])
        logging.log(logging.INFO, f'Items removed {items_removed}')

        # Close all opened exporters
        for exporter, csv_file in self.exporter_files.values():
            exporter.finish_exporting()
            csv_file.close()


    def _area_exporter(self, search_area):
        '''In case multiple search areas are active
        multiple exporters to be assigned
        Checks if 'search_area' exporter already exists
        if not, it's being created
        '''
        if search_area not in self.exporter_files:
            # Create exporter
            csv_file = open(f'data/{search_area}-{date.today()}.csv', 'wb+')
            exporter = CsvItemExporter(csv_file)
            exporter.start_exporting()
            self.exporter_files[search_area] = (exporter, csv_file)

            # Search for historical data
            self._get_previous_records(search_area)

        return self.exporter_files[search_area][0]


    def process_item(self, item, spider):
        self.items_processed += 1
        id = int(item['id'])
        if self.previous_records.get(id, False):
            self.items_already_exist += 1
            self.previous_records[id] = False
        else:
            # Clean data and export
            item['floor_area'] = clean.area(item['floor_area'])
            item['property_area'] = clean.area(item['property_area'])
            item['price'] = clean.price(item['price'])
            item['rooms'] = clean.rooms(item['rooms'])
            item['address'] = clean.postcode(item['address'])
            item['lat'], item['lon'] = self._get_coordinates(item['address'])

            exporter = self._area_exporter(spider.search_area)
            exporter.export_item(item)

        if self.previous_records.get(id, False):
            raise CloseSpider('Item not removed')

        logging.log(logging.DEBUG, f'Items processed {self.items_processed}')
        return item


    def _get_previous_records(self, search_area):
        '''Loads data from previous crawls. Compares items added/removed'''

        with os.scandir('data/') as files:
            for file in files:
                if not file.name.startswith('.')\
                    and file.is_file()\
                    and file.name.split('.')[-1] == 'csv'\
                    and '_removed' not in file.name\
                    and search_area in file.name:
                    self._load_previous_data(file.path)


    def _load_previous_data(self, file_path):
        with open(file_path) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.previous_records[int(row['id'])] = True


    def _get_coordinates(self, address):
        '''Gets address coordinates from Nomintim API'''

        url = 'https://nominatim.openstreetmap.org/search'
        params = {'q': address,
                  'format': 'json'}
        response = requests.get(url, params).json()
        if response:
            return response[0]['lat'], response[0]['lon']
        return None, None
