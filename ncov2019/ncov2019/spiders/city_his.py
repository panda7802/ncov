# -*- coding: utf-8 -*-
import datetime
import json
import logging
import traceback

import scrapy
from scrapy import Request

from ncov.models import ZoneInfo, CnovInfo, CnovHisInfo


def get_dict_int(d, key, data=0):
    try:
        if key not in d.keys() or d[key] is None:
            return data
        else:
            return int(d[key])
    except:
        logging.error(traceback.format_exc())
        return data


save_city = False


def ctrl_city_info(city_hist, p_id, s_time):
    """
    记录城市数据
    :return:
    """
    unknow_num = 1
    # 城市详情
    for c_item in city_hist:
        zone_info = ZoneInfo()
        cnov_info = CnovInfo()
        zone_info.name = c_item['name']
        zone_info.pid = p_id
        if 'id' in c_item.keys():
            zone_info.mid = c_item['id']
        else:
            zone_info.mid = ("%s_%d" % (p_id, unknow_num))
            unknow_num += 1

        cnov_info.confirmedNum = get_dict_int(c_item, 'confirmedNum')
        cnov_info.curesNum = get_dict_int(c_item, 'curesNum')
        cnov_info.deathsNum = get_dict_int(c_item, 'deathsNum')
        cnov_info.upd_time = s_time
        cnov_info.cid = zone_info.mid
        # try:
        if save_city:
            zone_info.save()
        cnov_info.save()
        # except:
        #     traceback.print_exc()
        print("\t\t城市：%s : %d , %d , %d" % (
            c_item['name'], cnov_info.confirmedNum, cnov_info.curesNum, cnov_info.deathsNum))


def ctrl_pro_his(series, p_id, s_time):
    """
    省历史数据
    :return:
    """
    for s_item in series:
        cnov_his_info = CnovHisInfo()
        cnov_his_info.confirmedNum = get_dict_int(s_item, 'confirmedNum')
        cnov_his_info.curesNum = get_dict_int(s_item, 'curesNum')
        cnov_his_info.deathsNum = get_dict_int(s_item, 'deathsNum')
        cnov_his_info.s_date = s_item['date']
        cnov_his_info.upd_time = s_time
        cnov_his_info.pid = p_id
        print("\t\t历史：%s : %d , %d , %d" % (
            cnov_his_info.s_date, cnov_his_info.confirmedNum, cnov_his_info.curesNum, cnov_his_info.deathsNum))
        cnov_his_info.save()


class CityHisSpider(scrapy.Spider):
    name = 'city_his'
    allowed_domains = ['i.snssdk.com']
    start_urls = ['https://i.snssdk.com/forum/home/v1/info/?activeWidget=1&forum_id=1656784762444839']

    # start_urls = ['https://i.snssdk.com/forum/ncov_data/?forum_id=1656388947394568&is_web_refresh=1&data_type=%5B6%5D&province_id=%5B%22320000%22%5D']

    def start_requests(self):
        if save_city:
            ZoneInfo.objects.all().delete()
        CnovInfo.objects.all().delete()
        CnovHisInfo.objects.all().delete()
        yield Request(url=self.start_urls[0])

    def parse(self, response):
        if response.status != 200:
            print("get err ,url : " + response.url)
            logging.error("get err ,url : " + response.url)
            return

        print("----------data-----------")
        print(response.body)
        s_json = response.body.decode('utf-8', 'ignore')
        dict_data = json.loads(s_json)
        print(dict_data)
        s_provinces_his = dict_data['forum']['extra']['ncov_string_list']
        provinces_data = json.loads(s_provinces_his)
        provinces_his = provinces_data['provinces']
        # print(s_city_his)
        # city_his = json.loads(s_city_his)
        # 数据由三部分构成，城市详情，省统计，省历史信息
        update_time = provinces_data['updateTime']
        s_time = datetime.datetime.fromtimestamp(update_time).strftime("%Y-%m-%d %H:%M:%S")
        # print(s_time)

        for item in provinces_his:
            # 省统计
            print("省统计"
                  " ：%s,%d,%d,%d" %
                  (item['name'], get_dict_int(item, 'confirmedNum'), get_dict_int(item, 'curesNum'),
                   get_dict_int(item, 'deathsNum')))
            # 省地区信息
            p_id = item['id']
            city_hist = item['cities']
            series = item['series']
            pro_info = ZoneInfo()
            pro_info.name = item['name']
            pro_info.mid = item['id']
            if save_city:
                pro_info.save()

            # 省数据
            cnov_pro_info = CnovInfo()
            cnov_pro_info.confirmedNum = get_dict_int(item, 'confirmedNum')
            cnov_pro_info.curesNum = get_dict_int(item, 'curesNum')
            cnov_pro_info.deathsNum = get_dict_int(item, 'deathsNum')
            cnov_pro_info.cid = p_id
            cnov_pro_info.upd_time = s_time
            cnov_pro_info.save()

            # 城市数据
            ctrl_city_info(city_hist, p_id, s_time)
            print("------------1----------")

            # 省历史信息
            pro_his_url = 'https://i.snssdk.com/forum/ncov_data/?forum_id=1656388947394568&is_web_refresh=1&data_type=%5B6%5D&province_id=%5B%22' + p_id \
                          + '0000%22%5D'
            print(pro_his_url)
            yield Request(pro_his_url, callback=self.parse_pro_his, meta={'pid': p_id,'s_time':s_time})
            # ctrl_pro_his(series, p_id, s_time)

            # # fixme 测试，只有一次
            # return

        # 获取全国数据
        print("-----获取全国数据------")
        china_his = provinces_data['nationwide']
        print(china_his)
        zoneinfo_chinas = ZoneInfo.objects.filter(mid=0)

        if len(zoneinfo_chinas) <= 0:
            zoneinfo_china = ZoneInfo()
            zoneinfo_china.upd_time = s_time
            zoneinfo_china.pid = 0
            zoneinfo_china.mid = 0
            zoneinfo_china.name = '中国'
            zoneinfo_china.save()
        else:
            zoneinfo_china = zoneinfo_chinas[0]

        mid_without_hb = '01'
        zoneinfo_withouthbs = ZoneInfo.objects.filter(mid=mid_without_hb)  # 除了湖北
        if len(zoneinfo_withouthbs) <= 0:
            zoneinfo_withouthb = ZoneInfo()
            zoneinfo_withouthb.upd_time = s_time
            zoneinfo_withouthb.pid = 0
            zoneinfo_withouthb.mid = mid_without_hb
            zoneinfo_withouthb.name = '除湖北'
            zoneinfo_withouthb.save()

        for s_item in china_his:
            cnov_his_info = CnovHisInfo()
            cnov_his_info.confirmedNum = get_dict_int(s_item, 'confirmedNum')
            cnov_his_info.curesNum = get_dict_int(s_item, 'curesNum')
            cnov_his_info.deathsNum = get_dict_int(s_item, 'deathsNum')
            cnov_his_info.s_date = s_item['date']
            cnov_his_info.upd_time = s_time
            cnov_his_info.pid = zoneinfo_china.pid
            print("\t\t全国历史：%s : %d , %d , %d" % (
                cnov_his_info.s_date, cnov_his_info.confirmedNum, cnov_his_info.curesNum, cnov_his_info.deathsNum))
            try:
                cnov_his_withouthb = CnovHisInfo()
                cnov_his_withouthb.pid = mid_without_hb
                cnov_his_hbs = CnovHisInfo.objects.filter(pid='42').filter(s_date=s_item['date'])
                if len(cnov_his_hbs) > 0:
                    cnov_his_withouthb.confirmedNum = get_dict_int(s_item, 'confirmedNum') - cnov_his_hbs[
                        0].confirmedNum
                    cnov_his_withouthb.curesNum = get_dict_int(s_item, 'curesNum') - cnov_his_hbs[0].curesNum
                    cnov_his_withouthb.deathsNum = get_dict_int(s_item, 'deathsNum') - cnov_his_hbs[0].deathsNum
                else:
                    cnov_his_withouthb.confirmedNum = get_dict_int(s_item, 'confirmedNum')
                    cnov_his_withouthb.curesNum = get_dict_int(s_item, 'curesNum')
                    cnov_his_withouthb.deathsNum = get_dict_int(s_item, 'deathsNum')
                cnov_his_withouthb.s_date = s_item['date']
                cnov_his_withouthb.upd_time = s_time
                cnov_his_withouthb.save()
                print("\t\t除湖北历史：%s : %d , %d , %d" % (
                    cnov_his_withouthb.s_date, cnov_his_withouthb.confirmedNum, cnov_his_withouthb.curesNum,
                    cnov_his_withouthb.deathsNum))
                cnov_his_info.save()
            except:
                logging.error(traceback.format_exc())
                traceback.print_exc()

    def parse_pro_his(self, response):
        """
        获取省份历史
        :param self:
        :param response:
        :return:
        """
        if response.status != 200:
            print("parse_pro_his get err ,url : " + response.url)
            logging.error("parse_pro_his get err ,url : " + response.url)
            return

        p_id = response.meta['pid']
        print('parse_pro_his : %s ' % p_id)
        print(response.body)
        s_json = response.body.decode('utf-8', 'ignore')
        dict_data = json.loads(s_json)
        # print(dict_data)

        try:
            s_provinces_his = dict_data['province_data'][p_id]
            provinces_data = json.loads(s_provinces_his)
            series = provinces_data['series']
            print(series)
            ctrl_pro_his(series, p_id, response.meta['s_time'])
        except:
            logging.error(traceback.format_exc())
