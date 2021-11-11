# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import re
import os
import csv
import requests
import logging
from datetime import date
from itemadapter import ItemAdapter
from scrapy.exporters import CsvItemExporter

class SaveToFilePipeline:
    def open_spider(self, spider):
        self.exporter_files = {}
        self.items_processed = 0
        self.items_already_exist = 0
        self.previous_records = []

        self.get_previous_records()

    def close_spider(self, spider):
        logging.log(logging.INFO, f'Items processed {self.items_processed}')
        logging.log(logging.INFO, f'Items existed {self.items_already_exist}')
        for exporter, csv_file in self.exporter_files.values():
            exporter.finish_exporting()
            csv_file.close()

    def _exporter_for_item(self, item):
        adapter = ItemAdapter(item)
        search_area = adapter['search_area']
        if search_area not in self.exporter_files:
            csv_file = open(f'data/{search_area}-{date.today()}.csv', 'wb+')
            exporter = CsvItemExporter(csv_file)
            exporter.start_exporting()
            self.exporter_files[search_area] = (exporter, csv_file)
        return self.exporter_files[search_area][0]

    def process_item(self, item, spider):
        self.items_processed += 1
        if item['id'] not in self.previous_records:
            item['address'] = self.remove_postcode_whitespace(item['address'])
            item['lat'], item['lon'] = self.get_coordinates(item['address'])

            exporter = self._exporter_for_item(item)
            exporter.export_item(item)
        else:
            self.items_already_exist += 1

        logging.log(logging.DEBUG, f'Items processed {self.items_processed}')
        return item

    def get_previous_records(self):
        with os.scandir('data/') as files:
            for file in files:
                if not file.name.startswith('.')\
                    and file.is_file()\
                    and file.name.split('.')[-1] == 'csv':
                    self.load_previous_data(file.path)

    def load_previous_data(self, file_path):
        with open(file_path) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.previous_records.append(row['id'])

    def remove_postcode_whitespace(self, address):
        '''Removes a whitespace from postal code into format 1234AB'''
        address_reg = re.match(r'(.*)(\d{4} \D{2})(.*)', address)
        groups = address_reg.groups()
        postal_code = groups[1].replace(' ', '')
        return groups[0] + postal_code + groups[2]

    def get_coordinates(self, address):
        url = 'https://nominatim.openstreetmap.org/search'
        params = {'q': address,
                  'format': 'json'}
        response = requests.get(url, params).json()
        if response:
            return response[0]['lat'], response[0]['lon']
        return None, None
