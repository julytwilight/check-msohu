# -*- coding: utf-8 -*-
import timeit
import urllib2
import gevent
from threading import Thread, RLock
from Queue import Queue
from gevent import monkey; monkey.patch_all()
from urlparse import urlparse, urljoin
# from socketpool import ConnectionPool
# from restkit import request, Connection
from bs4 import BeautifulSoup

# 页面入口 m.sohu.com导航页面
WEBSITE = 'http://m.sohu.com/c/395/?_once_=000025_top_daohang_v2&_smuid=B3c57lC0yV68YNhqcs02Ul&v=2'

# 域名
DOMAIN = 'http://m.sohu.com'

# 线程锁
mylock = RLock()

# 已访问的网址
visited = []
visited_num = 0

# 不进行检测的url
filter_href = [None, '#', '/', '?v=2&_once_=sohu_version_2', 'http://m.sohu.com/towww', '#top',
                '?v=1&_once_=sohu_version_1&_smuid=B3c57lC0yV68YNhqcs02Ul', 
                '?v=3&_once_=sohu_version_3&_smuid=B3c57lC0yV68YNhqcs02Ul',
                'http://m.sohu.com/towww?_smuid=B3c57lC0yV68YNhqcs02Ul&v=2',
                '?v=3&_once_=sohu_version_3&_smuid=Auo7Wsl5w5doUGTjNcK3Mp',
                '?v=1&_once_=sohu_version_1&_smuid=Auo7Wsl5w5doUGTjNcK3Mp']

# 读取导航页面
nav_text = urllib2.urlopen(WEBSITE).read()

# 页面soup
nav_soup = BeautifulSoup(nav_text)

# 获得需要检查的栏目
bd2 = nav_soup.find_all('p', 'bd2')

# 创建队列
q = Queue(0)
for b in bd2:
    if b.a:
        q.put(DOMAIN + b.a.get('href')) # 加入队列

# 线程类
class CheckThread(Thread):
    def __init__(self, qe, no):
        Thread.__init__(self)
        self._qe = qe # 队列
        self._no = no # 第几线程
        self.threads = 0 # 判断线程的数量

    def run(self):
        # 每运行一个线程线程+1
        self.threads += 1

        while True:
            if self._qe.qsize() > 0: # 如果列队中还有Url则继续线程继续执行
                self._work(self._qe.get(), self._no)
            else:
                # 当线程关闭-1
                self.threads -= 1
                # 如果线程都结束则关闭日志文件
                if self.threads == 0:
                    logging.shutdown()
                break

    def _work(self, url, no):
        check_page_links(url, no)

def check_page_links(url, no):
    print 'Worker: %s' % no

    # 读取页面链接
    text = urllib2.urlopen(url).read()
    soup = BeautifulSoup(text)
    links = soup.find_all('a')

    # 线程添加已检测url时进行线程锁
    mylock.acquire()
    visited.append(url)
    visited_num += 1
    mylock.release()
    jobs = []

    for link in links:
        href = link.get('href')

        # 过滤不合法的href
        if href in filter_href:
            continue
        elif href.find('javascript', 0, 10) != -1:
            continue

        # 获得完整的url
        correct_url = get_correct_url(href)

        # jobs.append(gevent.spawn(fetch, correct_url))

    # gevent.joinall(jobs)

# 获得完整的url
def get_correct_url(url):
    uhost = urlparse(url)
    
    if uhost.netloc == "":
        url = urljoin(DOMAIN, url)

    return url.encode('utf-8')

# set a pool with a gevent packend
# pool = ConnectionPool(factory=Connection, backend="gevent")

# urls = [
        # "http://yahoo.fr",
        # "http://google.com",
        # "http://friendpaste.com",
        # "http://benoitc.io",
        # "http://couchdb.apache.org"]

# allurls = []
# allurls.extend(urls)

# def fetch(u):
#     r = request(u, follow_redirect=True, pool=pool)
#     print "RESULT: %s: %s (%s)" % (u, r.status, len(r.body_string()))

# def extract():

#     jobs = [gevent.spawn(fetch, url) for url in allurls]
#     gevent.joinall(jobs)

# t = timeit.Timer(stmt=extract)
# print "%.2f s" % t.timeit(number=1)

if __name__ == '__main__':
    CheckThread(q, 1).start()
    CheckThread(q, 2).start()
