# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import os

import openpyxl as openpyxl
import scrapy
from openpyxl import Workbook


class NcovCityPipeline(object):

    def __init__(self):
        logging.debug("-------NcovCityPipeline __init__---------")

    def open_spider(self, spider):
        """
        开爬虫
        :param spider:
        :return:
        """
        logging.debug("-------NcovCityPipeline open_spider---------")

    def process_item(self, item, spider):
        self.add_line(item)
        return item

    def close_spider(self,spider):
        logging.debug("-------NcovCityPipeline close_spider---------")
