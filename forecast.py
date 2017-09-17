# coding: utf-8

import json
import os
import sys
import urllib2

import flask

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = flask.Flask(__name__)

#CHANNEL_ACCESS_TOKEN
line_bot_api = LineBotApi('CHANNEL_ACCESS_TOKEN')
#CANNEL_SECRET
handler = WebhookHandler('CANNEL_SECRET')


@app.route("/")
def hello():
    forecast()
    return "hello this page is nothing."


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = flask.request.headers['X-Line-Signature']

    # get request body as text
    body = flask.request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        flask.abort(400)

    return 'OK'

@handler.add(MessageEvent, message = TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(forecast()))

def forecast():
    try:
        citycode = sys.argv[1]
    except:
        citycode = '130010'
    responce = urllib2.urlopen('http://weather.livedoor.com/forecast/webservice/json/v1?city=%s' % citycode).read()
    resp = json.loads(responce)
    forecasts = resp['forecasts'][0]

    separate = '**************************'
    title = resp['title']
    description = resp['description']['text']
    date = forecasts['dateLabel'] + '(' + forecasts['date'] + ')'
    telop = forecasts['telop']
    maxtemp = u'最高気温: ' + forecasts['temperature']['max']['celsius'] + u'℃'

    #forecastmessage = separate + os.linesep + description + os.linesep + separate + os.linesep + date + os.linesep + telop + os.linesep + maxtemp + os.linesep + separate
    #forecastmessage = '**************************' + os.linesep + resp['title'] + '**************************' + os.linesep + resp['description']['text'] + '**************************' + os.linesep + forecasts['dateLabel'] + '(' + forecasts['date'] + ')' + os.linesep + forecasts['telop'] + os.linesep + u'最高気温: ' + forecasts['temperature']['max']['celsius'] + u'℃' + os.linesep + '**************************'

    if(resp is None):
        forecastmessage = u'本日分の天気予報はありません。'
    elif(forecasts['temperature']['max']['celsius'] is None):
        forecastmessage = '**************************' + os.linesep + resp[
            'title'] + '**************************' + os.linesep + forecasts['dateLabel'] + '(' + forecasts[
                          'date'] + ')' + os.linesep + forecasts['telop'] + os.linesep + '**************************'
    else:
        forecastmessage = '**************************' + os.linesep + resp[
            'title'] + '**************************' + os.linesep + forecasts['dateLabel'] + '(' + forecasts[
                              'date'] + ')' + os.linesep + forecasts['telop'] + os.linesep + u'最高気温: ' + \
                          forecasts['temperature']['max']['celsius'] + u'℃' + os.linesep + '**************************'

    return forecastmessage

if __name__ == "__main__":
    app.run()
