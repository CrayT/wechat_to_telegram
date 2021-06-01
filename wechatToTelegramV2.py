# encoding: utf-8
from html import unescape
from urllib.parse import urlparse, parse_qs
import subprocess
import requests
import telegram
from telegram.error import BadRequest
from telegram.utils.request import Request
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters
import itchat
from itchat.content import *
import json
from urllib.request import urlopen
from bs4 import BeautifulSoup
import  schedule
import _thread
import datetime
import time
from PIL import Image
from check12306 import run_file
# 申请telegram后获得的bot token
TELEGRAM_BOT_TOKEN = "769700212:AAGN02zWIsj4AVQ-p6sxmRZw8zuWtVDnjC4"
CHAT_ID = '728926819'
SUB_SECRET = "wsXT"
# 转发消息的群名, 直接复制就好
GROUP_WHITELIST = []
ALL_GROUP = True
# 要用代理啊，不然连不到telegram服务器啊
HTTP_PROXY = "socks5h://127.0.0.1:1086"

bot_instance = telegram.Bot(token = TELEGRAM_BOT_TOKEN,request = Request(proxy_url = HTTP_PROXY))

update_instance = Updater(bot = bot_instance)

def check_is_myself(msg):
    # friend=itchat.get_friends()
    # print(friend[0])
    # itchat.send_msg("hello",friend[0].UserName)
    if msg.User.UserName == "filehelper":
        return False
    return msg.FromUserName == itchat.originInstance.storageClass.userName


def get_name(msg):
    if hasattr(msg.User, "NickName"):
        name = msg.User.NickName
    else:
        name = msg.User.UserName
    print(name)
    return name


@itchat.msg_register([TEXT], isFriendChat = True)
def forward_personal_text(msg):
    global CHAT_ID
    name = get_name(msg)
    if not check_is_myself(msg):
        bot_instance.send_message(CHAT_ID,
                                  "[{name}]({url}) : {content}".format(
                                      name = name,
                                      url = "http://g3453raesr4dsafsdoogle.com?user={}".format(msg["FromUserName"]),
                                      content = msg.Content),
                                  parse_mode = "Markdown"
                                  )

@itchat.msg_register(TEXT, isGroupChat=True)
def forward_group_text(msg):
    global CHAT_ID
    if not check_is_myself(msg):
        group_name = unescape(msg.User.NickName)
        if not ALL_GROUP:
            if group_name not in GROUP_WHITELIST:
                return None
        bot_instance.send_message(CHAT_ID,
                                  "[{group}]({url})—[{user}]({url}) : {content}".format(
                                      group = group_name,
                                      url = "http://googl2r3rewaar3e.com?user={}".format(msg["FromUserName"]),
                                      user = msg.ActualNickName,
                                      content = msg.Content),
                                  parse_mode = "Markdown"
                                  )

@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO], isFriendChat = True, isGroupChat = True)
def forward_pic(msg):
    global CHAT_ID
    name = get_name(msg)
    if not check_is_myself(msg):
        if hasattr(msg, "IsAt"):
            if not ALL_GROUP:
                if unescape(name) not in GROUP_WHITELIST:
                    return None
            name += "—{}".format(msg.ActualNickName)
        bot_instance.send_message(CHAT_ID,
                                  "[{name}]({url}) sending a {typ}, loading~".format(
                                      name = name,
                                      url = "http://googsdfafewrqwele.com?user={}".format(msg["FromUserName"]),
                                      typ = msg["Type"]
                                  ),
                                  parse_mode="Markdown"
                                  )
        # save img
        msg.download(msg['FileName'])
        try:
            bot_instance.send_document(CHAT_ID, document = open('./{}'.format(msg['FileName']), 'rb'))
        except BadRequest:
            pass
        finally:
            subprocess.Popen("rm ./{}".format(msg['FileName']), shell=True)


def sub(bot, update):
    global CHAT_ID
    if update.message.text.split(maxsplit=1)[-1] == SUB_SECRET:
        CHAT_ID = update.message.chat_id
        update.message.reply_text("sub success")


def toggle(bot, update):
    global ALL_GROUP
    ALL_GROUP = not ALL_GROUP
    update.message.reply_text("success, {}".format("receive all" if ALL_GROUP else "filtered"))


def echo(bot, update):
    url = update.message["reply_to_message"]["entities"][0]["url"]
    qs = urlparse(url).query
    target = parse_qs(qs)["user"][0]
    print(target)
    if update.message.text: #发送文字
        try:
            reply_content = update.message["text"]
            itchat.send_msg(reply_content, target)
        except Exception as e:
            print(e)
    elif update.message.photo: #发送图片
        new_file = bot.get_file(update.message.photo[-1].file_id)
        new_file.download('tmp.jpg')
        itchat.send_image('tmp.jpg', target)
        subprocess.Popen("rm ./{}".format("tmp.jpg"), shell = True)

    elif update.message.sticker: #sticker
        file_id = update.message.sticker.file_id
        new_file = bot.get_file(file_id)
        new_file.download('sticker.webp')
        im = Image.open('sticker.webp').convert("RGB")
        im.save('sticker.jpg')
        itchat.send_image('sticker.jpg', target)
        subprocess.Popen("rm ./{}".format('sticker.jpg'), shell = True)
        subprocess.Popen("rm ./{}".format('sticker.webp'), shell = True)

    elif update.message.animation: #GIF
        file_id = update.message.animation.file_id
        file_name = update.message.animation.file_name
        new_file = bot.get_file(file_id)
        new_file.download(file_name)
        subprocess.call("ffmpeg -v -8 -i {} tmp.gif -hide_banner".format(file_name), shell = True)
        itchat.send_image('tmp.gif', target)
        subprocess.Popen("rm ./{}".format('tmp.gif'), shell = True)
        subprocess.Popen("rm ./{}".format(file_name), shell = True)

    elif update.message.document: #发送附件
        new_file = bot.get_file(update.message.document.file_id)
        filename=str(update.message.document.file_name)
        new_file.download(filename)
        itchat.send_file(filename,target)
        subprocess.Popen("rm ./{}".format(filename), shell = True)


def find(bot, update): #查找联系人
    name = update.message.text.split(maxsplit = 1)[-1]
    for ifriend in itchat.get_friends(): #拿到朋友列表
        name_l=[]
        name_l.append(ifriend.UserName)
        name_l.append(ifriend.NickName)
        name_l.append(ifriend.RemarkName)
        for item in name_l:
            if name in str(item): #只要任一个匹配即认为找到并返回
                mess = "[{name}](http://goo423sfadsg.com?user={url})".format(name = name_l[1],url = name_l[0])
                bot_instance.send_message(CHAT_ID, mess, parse_mode = "Markdown")
                return 
            else:
                pass
    
    for chatroom in itchat.get_chatrooms(): #查找群。需要在找不到联系人的前提下才会查找群聊。
        name_l = []
        name_l.append(chatroom.UserName)
        name_l.append(chatroom.NickName)
        if name in str(name_l[1]): #只要任一个匹配即认为找到并返回
            mess = "[{name}](http://goo423sfadsg.com?user={url})".format(name = name_l[1],url = name_l[0])
            bot_instance.send_message(CHAT_ID, mess, parse_mode = "Markdown")
            return 

def get_city_id(city): #匹配城市id
    with open('天气城市id.json','r') as f: #ubuntu
        tmp = json.load(f)
    for item in tmp.keys():
        if city == item:
            return tmp[item]['weatherCode']

def check_weather(place,flag): #改造，传入城市和flag，返回mess_now，flag为字符串，非数字。
    weather_id = get_city_id(place)
    print(weather_id)
    try:
        tp_now = requests.get('http://wthrcdn.etouch.cn/weather_mini?citykey=%s'%(weather_id)) #实况天气
        weather_now = tp_now.content.decode('utf-8')
        weather_now = json.loads(weather_now)
        weather_info = []

        if flag == '0': #默认查询当天
            tmp_dic = {}
            mess_now = "%s当前天气预报:\n当前温度:%s度\n"%(place,weather_now['data']['wendu'])
            
            tmp_dic = weather_now['data']['forecast'][0]
            fengli = tmp_dic['fengli'].split('[')[2].split(']')[0]

            weather_info.append("天气状况: "+tmp_dic["type"]+"\n"+tmp_dic['high']+"\n"+\
            tmp_dic['low']+"\n风向:"+tmp_dic["fengxiang"]+"\n风力:"+fengli+"\n\n")

        else:
            for i in range(1,int(flag)+1):
                tmp_dic = {}
                tmp_dic = weather_now['data']['forecast'][i]
                fengli = tmp_dic['fengli'].split('[')[2].split(']')[0]
                weather_info.append(tmp_dic['date']+":\n天气状况: "+tmp_dic["type"]+"\n"+tmp_dic['high']+"\n"+\
                tmp_dic['low']+"\n风向:"+tmp_dic["fengxiang"]+"\n风力:"+fengli+"\n\n")

            mess_now = "%s未来%s天天气预报:\n"%(place,flag)
            mess_now += "当前温度:%s度\n\n"%(weather_now['data']['wendu'])
        for item in weather_info:
                mess_now += item
    except exception as e:
        print(e)
        mess_now = '查询失败'
    return mess_now

def send_weather():#整合在这里发送,将发送名单归到dict，名字：地区，发送信息。调用check_weather，flag置0，
    with open('name_list.json','r') as f: #ubuntu
        name_list = json.load(f) #姓名:地区
    name_Username={} #姓名: Username
    name_messinfo={} #姓名:mess
    for name_tmp in name_list.keys():
        for ifriend in itchat.get_friends(): #拿到朋友列表
            name_l=[]
            name_l.append(ifriend.UserName)
            name_l.append(ifriend.NickName)
            name_l.append(ifriend.RemarkName)
            for item in name_l:
                if name_tmp in str(item): #只要任一个匹配即认为找到并返回
                    name_Username.update({name_tmp:name_l[0]})
        messinfo=check_weather(name_list[name_tmp],'0') #拿到天气信息
        name_messinfo.update({name_tmp:messinfo})
    for username in name_Username.keys(): #发送信息。
        itchat.send_msg(name_messinfo[username],name_Username[username])

def get_weather_bot(bot, update): #bot命令方式调用查询函数
    print(update.message.text)
    argg = update.message.text.split(maxsplit = 1)[-1]
    arg = argg.split()
    place = arg[0]
    flag = '0' #默认查询当前天气，默认flag为0；
    if len(arg) > 1:
        flag = arg[1] #第二个参数，值为1，2，3，4，当天，明天，后天。。。

    mess_now = check_weather(place,flag) #调用查询天气函数

    bot.send_message('728926819',mess_now) #向telegram bot发送信息
    itchat.send_msg(mess_now, itchat.originInstance.storageClass.userName) #给微信自己发信息

def get_12306_bot(bot, update): #查询车票 /tk 出发地 到达地 日期
    # print(update.message.text)
    argg = update.message.text.split(maxsplit = 1)[-1]
    arg = argg.split()

    from_station = arg[0] #拿参数
    to_station = arg[1]
    date = arg[2]

    mess = run_file(from_station , to_station , date) 
    bot.send_message('728926819',mess)

def get_weather():#已经弃用该方式
    resp = urlopen('http://www.weather.com.cn/weather1d/101020300.shtml')
    soup = BeautifulSoup(resp,'html.parser')

    today_weather_day = soup.find_all('p',class_ = "wea")[0].string
    today_weather_night = soup.find_all('p',class_ = "wea")[1].string
    today_temperature_high = soup.find_all('p',class_ = "tem")[0].span.string
    today_temperature_low = soup.find_all('p',class_ = "tem")[1].span.string
    
    mess = "上海宝山区今日天气:\n白天天气: %s\n夜间天气: %s\n最高温度: %s\n最低温度: %s"%(today_weather_day,today_weather_night,today_temperature_high,today_temperature_low)
    
    itchat.send_msg(mess, itchat.originInstance.storageClass.userName) #给自己发信息

def sch(p):
    schedule.every().day.at('19:00').do(send_weather) #早上8点定时发送
    while True:
        schedule.run_pending()#确保schedule一直运行
        time.sleep(1)

_thread.start_new_thread( sch, (1,))

dis = update_instance.dispatcher
sub_handler = CommandHandler("sub", sub)
toggle_handler = CommandHandler("t", toggle)
find_handler = CommandHandler("f", find) #查找联系人
get_weather_handler = CommandHandler("w", get_weather_bot) #查询天气
get_12306_handler = CommandHandler("tk", get_12306_bot) #查询12306车票
message_handler = MessageHandler(Filters.text | Filters.photo | Filters.sticker | Filters.document, echo)
dis.add_handler(find_handler)
dis.add_handler(sub_handler)
dis.add_handler(toggle_handler)
dis.add_handler(message_handler)
dis.add_handler(get_weather_handler)
dis.add_handler(get_12306_handler)

update_instance.start_polling()

itchat.auto_login(enableCmdQR = 2,hotReload = True)

itchat.run(True)
