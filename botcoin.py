#!/usr/bin/env python

import time
import httplib
import urllib2

from urlparse import urljoin
from urllib import urlencode

import json

API_TOKEN = '(your api token)'
ROOM_ID = '(your room id)'

API_URL_DEFAULT = 'https://api.hipchat.com/v1/'
FORMAT_DEFAULT = 'json'


class HipChat(object):
    """https://github.com/kurttheviking/python-simple-hipchat/blob/master/hipchat/__init__.py"""
    def __init__(self, token=None, url=API_URL_DEFAULT, format=FORMAT_DEFAULT):
        self.url = url
        self.token = token
        self.format = format
        self.opener = urllib2.build_opener(urllib2.HTTPSHandler())

    class RequestWithMethod(urllib2.Request):
        def __init__(self, url, data=None, headers={}, origin_req_host=None, unverifiable=False, http_method=None):
            urllib2.Request.__init__(self, url, data, headers, origin_req_host, unverifiable)
            if http_method:
                self.method = http_method

        def get_method(self):
            if self.method:
                return self.method
            return urllib2.Request.get_method(self)

    def method(self, url, method="GET", parameters=None, timeout=None):
        method_url = urljoin(self.url, url)

        if method == "GET":
            if not parameters:
                parameters = dict()

            parameters['format'] = self.format
            parameters['auth_token'] = self.token

            query_string = urlencode(parameters)
            request_data = None
        else:
            query_parameters = dict()
            query_parameters['auth_token'] = self.token

            query_string = urlencode(query_parameters)

            if parameters:
                request_data = urlencode(parameters)
            else:
                request_data = None

        method_url = method_url + '?' + query_string

        req = self.RequestWithMethod(method_url, http_method=method, data=request_data)
        response = self.opener.open(req, None, timeout).read()

        return json.loads(response)

    def list_rooms(self):
        return self.method('rooms/list')

    def message_room(self, room_id='', message_from='', message='', message_format='text', color='', notify=False):
        parameters = dict()
        parameters['room_id'] = room_id
        parameters['from'] = message_from[:15]
        parameters['message'] = message
        parameters['message_format'] = message_format
        parameters['color'] = color

        if notify:
            parameters['notify'] = 1
        else:
            parameters['notify'] = 0

        return self.method('rooms/message', 'POST', parameters)

def hipchat_broadcast(by='HipChat', message='Hello, World!', room_id=0):
    """Says random stuff on our Hipchat boards."""
    hip = HipChat(token=API_TOKEN)
    hip.method("rooms/message", method="POST",
               parameters={"room_id": room_id, "from": by,
                           "message": message, "message_format": "text"})



old_price = 0
while True:

    conn = httplib.HTTPConnection('api.bitcoincharts.com')
    conn.request("GET", "/v1/markets.json")
    res = conn.getresponse()
    data = res.read()

    prices = json.loads(data)

    usd_prices = filter(lambda x: x['currency'] == 'USD', prices)

    usd_sum = sum(map(lambda x: (x['bid'] or 0), usd_prices))

    price = usd_sum / len([x for x in usd_prices if x['bid'] is not None])
    if price > old_price:
        old_price = price

        hipchat_broadcast(
            'Botcoin', 
            "BITCOIN IS AT $%d!!" % price,
            ROOM_ID)

    time.sleep(1000)  # 17 minutes
