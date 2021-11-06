# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import logging
from itemadapter import ItemAdapter
from scrapy.exporters import CsvItemExporter

class SaveToFilePipeline:
    def open_spider(self, spider):
        self.exporter_files = {}
        logging.log(logging.INFO, 'Open spider')
        self.items_processed = 0

    def close_spider(self, spider):
        for exporter, csv_file in self.exporter_files.values():
            exporter.finish_exporting()
            csv_file.close()

    def _exporter_for_item(self, item):
        adapter = ItemAdapter(item)
        city = adapter['city']
        if city not in self.exporter_files:
            csv_file = open(f'data/{city}.csv', 'wb+')
            exporter = CsvItemExporter(csv_file)
            exporter.start_exporting()
            self.exporter_files[city] = (exporter, csv_file)
        return self.exporter_files[city][0]


    def process_item(self, item, spider):
        exporter = self._exporter_for_item(item)
        exporter.export_item(item)

        self.items_processed += 1
        logging.log(logging.INFO, f'Items processed {self.items_processed}')
        return item
