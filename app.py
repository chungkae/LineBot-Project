from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *



import requests
from bs4 import BeautifulSoup
import re
import random
import pandas as pd

import sys
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials


app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('your token')
# Channel Secret
handler = WebhookHandler('XXXXX')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


def ptt(bd):
    web='https://www.ptt.cc/bbs/'+bd+'/index.html'
    cookies = {'over18': '1'}
    apple = requests.get(web,cookies=cookies)
    pineapple = BeautifulSoup(apple.text,'html.parser')
    last = pineapple.select('div.btn-group-paging a')
    last_web = 'https://www.ptt.cc'+last[1]['href']
    apple = requests.get(last_web,cookies=cookies)
    pineapple = BeautifulSoup(apple.text,'html.parser')
    article = pineapple.select('div.title a')
    random.shuffle(article)
    re_imgur = re.compile('http[s]?://i.imgur.com/\w+\.(?:jpg)')
    for tit in article:
        apple = requests.get('https://www.ptt.cc'+tit['href'],cookies=cookies)
        images = re_imgur.findall(apple.text)
        if len(images)!=0:
            break
    num=random.randint(0,len(images)-1)
    return images[num]



# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):


    msg = event.message.text
    #print(type(msg))
    msg = msg.encode('utf-8')  
    if event.message.text.lower() in ["joke","笑","笑話"]:
        df = pd.read_csv('joke.csv')
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=df['joke'][random.randint(0,len(df)-1)]))
    elif event.message.text.lower() in ["hot","正","表特","sexy"]:
        a=ptt("Beauty")
        print(a)
        line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=a, preview_image_url=a))
    elif "讚" in event.message.text:  #可能有1MB的限制
        line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url='http://i.imgur.com/CS1FI7L.jpg', preview_image_url='http://i.imgur.com/CS1FI7L.jpg'))
    elif event.message.text.lower() in ["貓貓",'cat','貓']:
        a=ptt("cat")
        line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=a, preview_image_url=a))
    elif event.message.text.lower() in ["author","作者"]:
        Image_Carousel = TemplateSendMessage(
        alt_text='找不到頁面',
        template=ImageCarouselTemplate(
        columns=[
            ImageCarouselColumn(
                image_url="https://www.pngitem.com/pimgs/m/128-1280162_github-logo-png-cat-transparent-png.png",
                action=URITemplateAction(
                    label='MyGitHub',
                    uri='https://github.com/chungkae'
                )
            ),
            ImageCarouselColumn(
                image_url='https://pbs.twimg.com/profile_images/817234935106904064/-un1NXl3.jpg',
                action=URITemplateAction(
                    label='Adam_Kaggle',
                    uri='https://www.kaggle.com/chungkae0406'
                )
            )
        ]
    )
    )
        line_bot_api.reply_message(event.reply_token,Image_Carousel)
    elif ',' in event.message.text:
        try:
            # 連結google sheet
            scopes = ["https://spreadsheets.google.com/feeds"]
            credentials = ServiceAccountCredentials.from_json_keyfile_name("forLinebot-4148025ab8ae.json", scopes)
            client = gspread.authorize(credentials)
            # 網址的key
            sheet = client.open_by_key("1_VDqxPO3vKaiOIqDTFqtK8hayVdB3DE4n6FBgvYxt9M").sheet1
            # 必要欄位
            miles = sheet.col_values(1)
            per = sheet.col_values(4)
            day = sheet.col_values(3)
            days = sheet.col_values(5)
            # 整理輸入資訊
            aa = event.message.text.split(',')
            aa.extend([datetime.date.today().strftime("%Y/%m/%d"),round((float(aa[0])-float(miles[-1]))/float(aa[1]),2),(datetime.datetime.today()-datetime.datetime.strptime(day[-1],"%Y/%m/%d")).days])
            sheet.append_row(aa)
            rp = f'本次平均耗油: {aa[3]} \n過去3次平均耗油:\n{str(per[-3:])} \n距上次加油天數: {aa[4]}天\n過去3次加油天數:\n{str(days[-3:])}'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=rp))
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="格式錯誤!\n輸入格式為:公里數,公升數 \nex:184250,31.01"))
    elif event.message.text.lower() == 'oil':
        try:
            # 連結google sheet
            scopes = ["https://spreadsheets.google.com/feeds"]
            credentials = ServiceAccountCredentials.from_json_keyfile_name("forLinebot-4148025ab8ae.json", scopes)
            client = gspread.authorize(credentials)
            # 網址的key
            sheet = client.open_by_key("1_VDqxPO3vKaiOIqDTFqtK8hayVdB3DE4n6FBgvYxt9M").sheet1
            # 必要欄位
            per = sheet.col_values(4)
            day = sheet.col_values(3)
            rp = f'過去3次平均耗油:\n{str(per[-3:])} \n過去3次加油日期:\n{str(day[-3:])}'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=rp))
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="google sheet連結有誤！"))
    
    elif event.message.text.lower() == 'teach':
        rtext = f"""--- 指令教學 ---\n
        - hot or 表特\n  > 心情差？爬表特回覆美照\n
        - joke or 笑話\n  > 笑一下吧！隨機回覆則笑話\n
        - cat or 貓貓\n  > 需要療癒？爬貓版回覆照片\n
        - news or 新聞\n  > news?爬取自由時報最新新聞\n
        - author or 作者\n  > 看誰這麼無聊？作者資訊\n
        - key 哩程_公升\n  > Lancer！紀錄加油看油耗\n
        - oil\n  > 該換車？Lancer最近油耗\n
        - teach\n  > 再教一次!"""
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=rtext))

    elif event.message.text.lower() in ["news",'新聞']:
        # 簡單爬自由時報即時新聞一則
        url = 'http://news.ltn.com.tw/list/breakingnews'
        html = requests.get(url)
        sp = BeautifulSoup(html.text, 'html.parser')
        data1 = sp.select("a.tit")
        for j in data1[:1]:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=j['href']))
        
    elif event.message.text == "貼圖":
        line_bot_api.reply_message(event.reply_token,StickerSendMessage(package_id=1, sticker_id=2))
    elif event.message.text == "圖片":
        line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url='圖片網址', preview_image_url='圖片網址'))
    elif event.message.text == "影片":
        line_bot_api.reply_message(event.reply_token,VideoSendMessage(original_content_url='影片網址', preview_image_url='預覽圖片網址'))
    elif event.message.text == "音訊":
        line_bot_api.reply_message(event.reply_token,AudioSendMessage(original_content_url='音訊網址', duration=100000))
    else:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="您所輸入的["+event.message.text+"],目前沒有設定功能唷！"))
        


import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
