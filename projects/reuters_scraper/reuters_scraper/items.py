# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ReutersScraperItem(scrapy.Item):
    title = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()
    snapshot_time = scrapy.Field()
    section = scrapy.Field()
    
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
