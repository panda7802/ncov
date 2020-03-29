# -*- coding: utf-8 -*-
import datetime
import json
import logging

import scrapy
# from ncov2019.pipelines import HisItem
from ncov2019.items import HisItem


class GetHisSpider(scrapy.Spider):
    name = 'get_world_his'
    allowed_domains = ['i.snssdk.com']
    start_urls = ['https://i.snssdk.com/forum/ncov_data/?country_id=%5B%22USA%22%5D&country_name=%E7%BE%8E%E5%9B%BD&click_from=overseas_epidemic_tab_list&data_type=%5B1%2C4%2C5%2C6%2C7%5D&policy_scene=USA']

    def parse(self, response):
        print("----------data-----------")
        print(response.body)
        s_json = response.body.decode('utf-8', 'ignore')
        dict_data = json.loads(s_json)
        print(dict_data)
