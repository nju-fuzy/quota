# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SpeciallistItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    department = scrapy.Field()
    sub_department = scrapy.Field()
    hospital = scrapy.Field()
    disease = scrapy.Field()
    speciallist = scrapy.Field()
