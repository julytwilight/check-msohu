# -*- coding: utf-8 -*-
import os
import logging
import time
from urllib import urlopen
from urlparse import urlparse, urljoin
from httplib import HTTP
from bs4 import BeautifulSoup
from Queue import Queue
from threading import Thread, RLock

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
nav_text = urlopen(WEBSITE).read()

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


class CheckThread(Thread):
    def __init__(self, qe, no):
        Thread.__init__(self)
        self._qe = qe # 队列
        self._no = no # 第几线程

    def run(self):
        while True:
            if self._qe.qsize() > 0:
                self._work(self._qe.get(), self._no)
            else:
                logging.shutdown()
                break

    def _work(self, url, no):
        check_page_links(url, no)


def check_page_links(url, no):
    print 'Worker: %d' % no

    text = urlopen(url).read()
    soup = BeautifulSoup(text)
    links = soup.find_all('a')

    # 线程添加已检测url时进行线程锁
    mylock.acquire()
    visited.append(url)
    mylock.release()

    print '进入页面: %s' % url

    for link in links:
        href = link.get('href')
        if href in filter_href:
            continue
        elif href.find('javascript', 0, 10) != -1:
            continue

        correct_url = get_correct_url(href)

        get_url_msg(correct_url)

        if correct_url.find('http://m.sohu.com/', 0, 19) == 0:
            if correct_url not in visited:
                check_page_links(correct_url, no)


def get_correct_url(url):
    uhost = urlparse(url)
    
    if uhost.netloc == "":
        url = urljoin(DOMAIN, url)

    return url


# 检查链接的有效性并生成信息
def get_url_msg(url):
    # 生成错误信息
    message = '\n'
    try:
        # 检查网址的开始时间
        utime = time.time()
        code = urlopen(url).getcode()
        if code in [200, 302]:
            message += (url + ': 成功访问')
            message += '\n' + '-' * 50 + '\n'
        else:
            message += (url + ': 链接失效, 错误编码: %d ' % code + '\n')
            message += '请求用时%f' % (time.time() - utime)
            message += '\n' + '#' * 50 + '\n'
            write_log('warning', message)
    except Exception, e:
        message += (str(e) + '\n')
        message += ('错误url:' + url)
        message += '\n' + '*' * 50 + '\n'
        write_log('error', message)
    finally:
        print message


def write_log(log_type, message):
    if log_type == 'error':
        logging.error(message)
    elif log_type == 'warning':
        logging.warning(message)


if __name__ == '__main__':
    for i in range(0, WORKS_NUM):
        CheckThread(q, i + 1).start()