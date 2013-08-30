# -*- coding: utf-8 -*-
import os
import logging
import time
import urllib2
from urlparse import urlparse, urljoin
from httplib import HTTP
from bs4 import BeautifulSoup
from Queue import Queue
from threading import Thread, RLock
from random import choice

# ip代理
iplist = ['1.9.189.65:3128', '27.24.158.130:80', '27.24.158.154:80']

# 已访问的网址
visited = []

# 定义线程的数量
WORKS_NUM = 3

# 页面入口 m.sohu.com导航页面
WEBSITE = 'http://m.sohu.com/c/395/?_once_=000025_top_daohang_v2&_smuid=B3c57lC0yV68YNhqcs02Ul&v=2'

# 域名
DOMAIN = 'http://m.sohu.com'

# 线程锁
mylock = RLock()

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

# 设置log
logging.basicConfig(filename = os.path.join(os.getcwd(), time.strftime('%Y-%m-%d-') + 'log.txt'),
        level = logging.WARN, filemode = 'a', format = '%(asctime)s - %(levelname)s: %(message)s')

# 不进行检测的url
filter_href = [None, '#', '/', '?v=2&_once_=sohu_version_2', 'http://m.sohu.com/towww', '#top',
                '?v=1&_once_=sohu_version_1&_smuid=B3c57lC0yV68YNhqcs02Ul', 
                '?v=3&_once_=sohu_version_3&_smuid=B3c57lC0yV68YNhqcs02Ul',
                'http://m.sohu.com/towww?_smuid=B3c57lC0yV68YNhqcs02Ul&v=2',
                '?v=3&_once_=sohu_version_3&_smuid=Auo7Wsl5w5doUGTjNcK3Mp', 
                '?v=1&_once_=sohu_version_1&_smuid=Auo7Wsl5w5doUGTjNcK3Mp']


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
    print 'Worker: %d' % no

    # 读取页面链接
    text = urllib2.urlopen(url).read()
    soup = BeautifulSoup(text)
    links = soup.find_all('a')

    # 线程添加已检测url时进行线程锁
    mylock.acquire()
    visited.append(url)
    mylock.release()

    print '进入页面: %s' % url

    for link in links:
        href = link.get('href')

        # 过滤不合法的href
        if href in filter_href:
            continue
        elif href.find('javascript', 0, 10) != -1:
            continue

        # 获得完整的url
        correct_url = get_correct_url(href)

        # 检查链接有效性
        get_url_msg(correct_url)

        # 如果此url是m.sohu.com域下的url 并且 没有被检测过递归检查
        if correct_url.find('http://m.sohu.com/', 0, 19) == 0:
            if correct_url not in visited:
                try:
                    check_page_links(correct_url, no)
                except Exception, e:
                    write_log('error', str(e), correct_url)


# 获得完整的url
def get_correct_url(url):
    uhost = urlparse(url)
    
    if uhost.netloc == "":
        url = urljoin(DOMAIN, url)

    return url.encode('utf-8')


# 检查链接的有效性并生成信息
def get_url_msg(url):
    ip = choice(iplist)

    proxy_support = urllib2.ProxyHandler({'http:':'http://' + ip})
    opener = urllib2.build_opener(proxy_support)
    urllib2.install_opener(opener)

    print '\nURL: %s\n' % url

    try:
        # 检查网址的开始时间
        utime = time.time()
        code = urllib2.urlopen(url).getcode()
        if code in [200, 302]:
            print '访问成功'
            print '\n' + '-' * 50 + '\n'
        else:
            print 'Error Code: %s' % code
            print '\n' + '#' * 50 + '\n'
            # 写入日志
            write_log('warning', code, url, time.time() - utime)
    except Exception, e:
        print str(e)
        print '\n' + '*' * 50 + '\n'
        # 写入日志
        write_log('error', str(e), url, time.time() - utime)

    time.sleep(1)


# 写入日志
def write_log(log_type, message, url, run_time=0.0):
    logger = '\n%s\n%s\n%f\n%s\n' % (url, message, run_time, '-'*50)
    if log_type == 'error':
        logging.error(logger)
    elif log_type == 'warning':
        logging.warning(logger)


if __name__ == '__main__':
    for i in range(0, WORKS_NUM):
        CheckThread(q, i + 1).start()

