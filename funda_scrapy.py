import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def get_data(filters):
    process = CrawlerProcess(get_project_settings())

    # default search criteria
    search_criteria = ['amsterdam',     #city
                       '150000-550000', #price range
                       'woonhuis',      #type
                       '+30km'          #distance
                       ]

    for i in range(1, len(filters)):
        search_criteria[i-1] = filters[i]

    process.crawl('funda', search_criteria=search_criteria)
    process.start()  # the script will block here until the crawling is finished


if __name__ == '__main__':
    get_data(sys.argv)
