# -*- coding: utf-8 -*-
import logging
import re
import traceback

import scrapy
from django.db.models import Q
from scrapy import Request

from ncov.models import ZoneInfo


class GetCityInfoSpider(scrapy.Spider):
    name = 'get_city_info'
    allowed_domains = ['baike.baidu.com']
    start_urls = ['http://baike.baidu.com/']
    # https://i.snssdk.com/feoffline/hot_list/template/hot_list/forum_share.html?forum_id=1656388947394568&is_web_refresh=1

    def start_requests(self):
        # zone_infos = ZoneInfo.objects.all().filter(people=0)  # .filter(~Q(pid=0)).filter(name='巫溪')  # .filter(people=0)
        zone_infos = ZoneInfo.objects.all()#.filter(name='山东')
        for index, item in enumerate(zone_infos):
            # if index >= 2:
            #     return
            url = "https://baike.baidu.com/item/%s" % item.name
            yield Request(url=url, meta={'zone_info': item})
        fixs = ['', '省', '市', '县', '区', '州']
        for fix in fixs:
            # 如果是城市找不到，就在地名后面加“市”
            zone_infos = zone_infos.filter(people=0)
            for index, item in enumerate(zone_infos):
                # if index >= 2:
                #     return
                # print(item.pid)
                if item.pid != 0 and item.pid != '0':
                    url = "https://baike.baidu.com/item/%s%s" % (item.name, fix)
                    print(url)
                    yield Request(url=url, meta={'zone_info': item})
                else:
                    url = "https://baike.baidu.com/item/%s省" % item.name
                    yield Request(url=url, meta={'zone_info': item})

    def parse(self, response):
        if response.status != 200:
            print("get err ,url : " + response.url)
            logging.error("get err ,url : " + response.url)
            return

        zone_info = response.meta['zone_info']
        print("%s---" % zone_info.name)
        # items = response.xpath('//*[@class="basicInfo-item value"]')
        # items = response.xpath('//*[@class="basicInfo-block basicInfo-left"]')
        items = response.xpath("//dl[contains(@class,'basicInfo-block basicInfo-')]//text()").extract()
        # print(len(items))
        # return
        start_search_people = False
        for index, item in enumerate(items):
            # print(item)
            # print(len(str(item).strip()))
            tag = "".join(item.split()).strip().replace("\n", "")
            if str(tag) == '人口':
                # 找到人口TAG
                start_search_people = True
                continue
            if start_search_people and len(str(item).strip()) > 0:
                # 找到人口数值
                people = 0
                nums = re.findall(r"\d+\.?\d*", tag)
                if len(nums) > 0:
                    people = nums[0]
                    if tag.find("亿") >= 0:
                        people = int(float(people) * 100000000)
                    elif tag.find("万") >= 0:
                        people = int(float(people) * 10000)

                if people == 0:
                    nums = re.findall(r"\d+", tag)
                    if len(nums) > 0:
                        people = nums[0]

                    if tag.find("亿") >= 0:
                        people = int(float(people) * 100000000)
                    elif tag.find("万") >= 0:
                        people = int(float(people) * 10000)
                # if tag.find("万") >= 0:
                #     people = int(float(tag[tag.find("[0-9]"):tag.find("万")]) * 10000)
                #     print("人口", people)
                # elif tag.find("人") >= 0:
                #     people = int(float(tag[:tag.find("人")]))
                #     print("人口", people)
                # else:
                #     print("=========", tag)
                print("人口 : %d" % people)
                start_search_people = False
                zone_info.people = people
                zone_info.save()
