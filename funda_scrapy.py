from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def get_data():
    process = CrawlerProcess(get_project_settings())

    # 'followall' is the name of one of the spiders of the project.
    search_criteria = ['rotterdam',     #city
                       '250000-350000', #price range
                       'woonhuis',      #type
                       '+30km'          #distance
                       ]
    process.crawl('funda', search_criteria=search_criteria)
    process.start()  # the script will block here until the crawling is finished


if __name__ == '__main__':
    get_data()
