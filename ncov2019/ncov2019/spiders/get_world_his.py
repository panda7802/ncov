# -*- coding: utf-8 -*-
import datetime
import json
import logging
import traceback

import scrapy

# from ncov2019.pipelines import HisItem
from scrapy import Request

from ncov.models import ZoneInfo, CnovHisInfo
from ncov2019.spiders.city_his import get_dict_int


class GetHisSpider(scrapy.Spider):
    name = 'get_world_his'
    allowed_domains = ['i.snssdk.com']
    start_urls = [
        'https://i.snssdk.com/forum/ncov_data/?country_id=%5B%22USA%22%5D&country_name=%E7%BE%8E%E5%9B%BD&click_from=overseas_epidemic_tab_list&data_type=%5B1%2C4%2C5%2C6%2C7%5D&policy_scene=USA']

    def parse(self, response):
        print("----------data-----------")
        print(response.body)
        try:
            s_json = response.body.decode('utf-8', 'ignore')
            dict_data = json.loads(s_json)
            overseas_data = json.loads(dict_data['overseas_data'])
            print(overseas_data)
            update_time = overseas_data['updateTime']
            s_time = datetime.datetime.fromtimestamp(int(update_time)).strftime("%Y-%m-%d %H:%M:%S")
            print(s_time)
            country = overseas_data['country']
            for item in country:
                print("%s : %s , %s" % (item['id'], item['code'], item['name']))
                zi_country = ZoneInfo.objects.filter(mid=item['id'])
                if len(zi_country) <= 0:
                    zi_country = ZoneInfo()
                    zi_country.upd_time = s_time
                    zi_country.pid = -1
                    zi_country.mid = item['id']
                    zi_country.name = item['name']
                    zi_country.save()
                else:
                    zi_country = zi_country[0]
                country_url = 'https://i.snssdk.com/forum/ncov_data/?country_id=%5B%22' \
                              + zi_country.mid + '%22%5D&country_name=' \
                              + zi_country.name + '&click_from=overseas_epidemic_tab_list&data_type=%5B1%2C4%2C5%2C6%2C7%5D&policy_scene=' + zi_country.mid
                print(country_url)
                yield Request(country_url, callback=self.parse_country,
                              meta={'zi_country': zi_country, 's_time': s_time})

                # # fixme 只看一个城市
                # return
        except:
            traceback.print_exc()

    def parse_country(self, response):
        print("----------parse_country-----------")
        print(response.body)
        try:
            zi_country = response.meta['zi_country']
            mid = zi_country.mid
            print("%s历史" % zi_country.name)
            s_time = response.meta['s_time']
            s_json = response.body.decode('utf-8', 'ignore')
            dict_data = json.loads(s_json)
            # print(dict_data)
            country_data = json.loads(dict_data['country_data'][mid])
            # print(country_data)
            series = country_data['series']
            for s_item in series:
                cnov_his_info = CnovHisInfo()
                cnov_his_info.confirmedNum = get_dict_int(s_item, 'confirmedNum')
                cnov_his_info.curesNum = get_dict_int(s_item, 'curesNum')
                cnov_his_info.deathsNum = get_dict_int(s_item, 'deathsNum')
                cnov_his_info.s_date = s_item['date']
                cnov_his_info.upd_time = s_time
                cnov_his_info.pid = mid
                print("\t\t%s : %d , %d , %d" % (
                    cnov_his_info.s_date, cnov_his_info.confirmedNum, cnov_his_info.curesNum, cnov_his_info.deathsNum))
                cnov_his_info.save()

        except:
            traceback.print_exc()
