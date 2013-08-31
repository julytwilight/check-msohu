# -*- coding: utf-8 -*-
import httplib, urllib, urlparse
from sgmllib import SGMLParser

# 解析指定的网页的html，得到该页面的超链接列表
class URLLister(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.urls = []

    def start_a(self, attrs):
        href = [v for k, v in attrs if k=='href']
        if href:
            self.urls.extend(href)

# 遍历超链接列表，并逐个的发送请求，判断接收后的代码，200为正常，其他为不正常
def fetch(host):
        usock = urllib.urlopen(host)
        parser = URLLister()
        print len(parser.urls)
        parser.feed(usock.read())
        uhost = urlparse.urlparse(host)
        len(parser.urls)
        exit()
        for url in parser.urls:
            print url
            # up = urlparse.urlparse(url)
            # print up
            # #因为超链接有两种方式：一种是直接的http://...... 一种是相对路径，/.../sample.html
            # #所以要分别处理
            # if up.netloc =="":
            #     http = httplib.HTTP(uhost.netloc)
            #     http.putrequest("GET", "/"+up.path+"?"+up.params+up.query+up.fragment)
            #     http.putheader("Accept", "*/*")
            #     http.endheaders()
            #     print http
            # else:
            #     http = httplib.HTTP(up.netloc)
            #     http.putrequest("GET", up.path+"?"+up.params+up.query+up.fragment)
            #     http.putheader("Accept", "*/*")
            #     http.endheaders()
            #     print http

            # errcode, errmsg, headers = http.getreply()
            # if errcode == 200:
            #     print url," : ok"
            # else:
            #     print url," : ",errcode


fetch('http://m.sohu.com/c/395/?_once_=000025_top_daohang_v2&_smuid=B3c57lC0yV68YNhqcs02Ul&v=2')