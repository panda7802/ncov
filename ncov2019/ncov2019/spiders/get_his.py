# -*- coding: utf-8 -*-
import datetime
import json
import logging

import scrapy

from ncov2019.pipelines import HisItem
from ncov.models import ZoneInfo


class GetHisSpider(scrapy.Spider):
    name = 'get_his'
    allowed_domains = ['i.snssdk.com']
    start_urls = ['https://i.snssdk.com/forum/home/v1/info/?activeWidget=1&forum_id=1656784762444839']

    def parse(self, response):
        if response.status != 200:
            print("get err ,url : " + response.url)
            logging.error("get err ,url : " + response.url)
            return

        s_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        print("----------data-----------")
        print(response.body)
        s_json = response.body.decode('utf-8', 'ignore')
        dict_data = json.loads(s_json)
        print(dict_data)
        s_detail = dict_data['forum']['extra']['ncov_string_list']
        d_detail = json.loads(s_detail)
        all_sure = 0
        all_dead = 0
        all_ok = 0
        all_maybe = 0
        for index, item in enumerate(d_detail):
            # print("%d : %s " % (index, item))
            item_details = item.split(" ")
            res_item = HisItem()
            res_item['sure'] = 0
            res_item['dead'] = 0
            res_item['ok'] = 0
            res_item['maybe'] = 0
            res_item['time_now'] = s_time
            for detail_index, item_detail in enumerate(item_details):
                # print("1.%d : %s" % (index, item_detail))
                if 0 == detail_index:
                    res_item['province'] = item_detail

                if item_detail.find('确诊') >= 0:
                    res_item['sure'] = int(item_detail.replace('确诊', '').replace('例', ''))

                if item_detail.find('死亡') >= 0:
                    res_item['dead'] = int(item_detail.replace('死亡', '').replace('例', ''))

                if item_detail.find('治愈') >= 0:
                    res_item['ok'] = int(item_detail.replace('治愈', '').replace('例', ''))

                if item_detail.find('疑似') >= 0:
                    res_item['maybe'] = int(item_detail.replace('疑似', '').replace('例', ''))

            # print(res_item)
            yield res_item
            all_sure += res_item['sure']
            all_dead += res_item['dead']
            all_ok += res_item['ok']
            all_maybe += res_item['maybe']

        # print("%d,%d,%d" % (all_sure, all_dead, all_ok))
        all_item = HisItem()
        all_item['province'] = '全国'
        all_item['sure'] = all_sure
        all_item['dead'] = all_dead
        all_item['ok'] = all_ok
        all_item['maybe'] = all_maybe
        all_item['time_now'] = s_time
        yield all_item
