--delete  from ncov_zoneinfo;delete from ncov_cnovinfo;

select c.name                                                          as '省',
       b.name                                                          as '市',
       b.people                                                        as '人口',
       a.confirmedNum                                                  as '确诊人数',
       a.curesNum                                                      as '治愈人数',
       a.deathsNum                                                     as '死亡人数',
       ROUND(ifnull((a.curesNum + 0.0) / a.confirmedNum, 0) * 100, 2)  as '治愈率',
       ROUND(ifnull((a.deathsNum + 0.0) / a.confirmedNum, 0) * 100, 2) as '死亡率',
       ROUND(ifnull((a.curesNum + 0.0) / b.people, 0) * 10000, 6)        as '确诊率'
from ncov_cnovinfo a,
     ncov_zoneinfo b,
     ncov_zoneinfo c
where a.cid = b.mid
  and b.pid = c.mid
 -- and b.name = '南京'
--order by 确诊人数 desc
order by "确诊率" desc
--order by 死亡人数 desc
--order by 治愈率 desc, 确诊人数 asc
--order by 死亡率 desc , 确诊人数 desc
