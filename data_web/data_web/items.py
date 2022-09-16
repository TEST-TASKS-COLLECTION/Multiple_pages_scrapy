# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DataWebItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    ph_num = scrapy.Field()
    email = scrapy.Field()
    s_type = scrapy.Field()
    addr_1 = scrapy.Field()
    addr_2 = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
