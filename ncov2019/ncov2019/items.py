# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Ncov2019Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class CityHisItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    curesNum = scrapy.Field()
    name = scrapy.Field()
    confirmedNum = scrapy.Field()
    deathsNum = scrapy.Field()
    provinces = scrapy.Field()


class HisItem(scrapy.Item):
    # 时间
    time_now = scrapy.Field()
    # 地区
    province = scrapy.Field()
    # 确诊
    sure = scrapy.Field()
    # 死亡
    dead = scrapy.Field()
    # 治愈
    ok = scrapy.Field()
    # 疑似
    maybe = scrapy.Field()