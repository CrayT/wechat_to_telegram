#! /usr/bin/env python3
#encoding:utf-8
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
import requests
import re
from json import loads
import json
from configparser import ConfigParser
disable_warnings(InsecureRequestWarning) 
def cli(from_station, to_station, date):
    url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.8955'
    r = requests.get(url, verify=False)
    stations = re.findall(r'([\u4e00-\u9fa5]+)\|([A-Z]+)', r.text)
    station = dict(stations)
    from_station = station.get(from_station)
    to_station = station.get(to_station)
    date = date
    print(to_station)
    url = 'https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(
        date, from_station, to_station
    )
    r = requests.get(url, verify=False)
    rows = r.json()['data']['result']
    mapp = r.json()['data']['map']
    l = []
    for row in rows:
        listt = []
        listt = row.split('|')
        if "列车停运" in listt:
            pass
        else:
            url_price='https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice?train_no={}&from_station_no={}&to_station_no={}&seat_types={}&train_date={}'.format(
            listt[2],listt[16],listt[17],listt[35],date
            )
            rw={}       
            
            rw['station_train_code']=listt[3]

            rw['from_station_name']=mapp[listt[6]]
            rw['to_station_name']=mapp[listt[7]]

            rw['start_time']=listt[8]
            rw['arrive_time']=listt[9]

            rw['time']=listt[10]

            rw['sw_num']=listt[32]
            rw['ydz_num']=listt[31]
            rw['edz_num']=listt[30]
            rw['yz_num']=listt[29]
            rw['yw_num']=listt[28]
            rw['wz_num']=listt[26]
            rw['rz_num']=listt[24]
            rw['rw_num']=listt[23]
  
            l.append(rw)
    return l

def changeKey (lis): #更换关键字为中文
    listt={}
    key=['station_train_code','from_station_name','to_station_name','start_time','arrive_time','time','sw_num','ydz_num','edz_num','rw_num','yw_num','rz_num','yz_num','wz_num']
    ll = ['车次', '出发站','到达站', '出发时','到达时', '历时', '商务', '一等座', '二等座',  '软卧',  '硬卧', '软座', '硬座', '无座']
    for i in range(len(key)):
        listt.update({ll[i]:lis[key[i]]})
    return listt

def run_file(from_station , to_station , date_set): 
    date = date_set  #拿到日历的日期
    dic = cli(from_station , to_station , date)    #调用识别文件函数
    mess_info = ''
    key_index=['车次', '出发站','到达站', '出发时','到达时', '历时']
    for j in range(len(dic)):
        list_tmp = changeKey (dic[j]) #dict
        key_tmp = [] #必有的关键字
        dict_tmp = {} #整理返回信息，车次，出发时间，到达时间，耗时，车次新词
        for key in list_tmp.keys():
            if list_tmp[key] == '' or list_tmp[key] == '无': #删除无座的坐席
                key_tmp.append(key)
        for item in key_tmp: #删除空的关键字
            list_tmp.pop(item)
        for item in key_index: #将必有信息加入字符串
            mess_info += item + ':' + list_tmp[item] + '\n'
        for item in key_index: #然后删掉已经加入的关键字
            list_tmp.pop(item)
        for key in list_tmp.keys(): #加入剩余的信息
            mess_info += key +':'+ list_tmp[key] + '\n'
        mess_info += '\n'

    return mess_info