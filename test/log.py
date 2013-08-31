# -*- coding: utf-8 -*-
import logging
import os
import time

try:
    print a
except Exception, e:
    print str(e)
    exit()


logging.basicConfig(filename = os.path.join(os.getcwd(), time.strftime('%Y-%m-%d') + 'log.txt'),
        level = logging.WARN, filemode = 'a', format = '%(asctime)s - %(levelname)s: %(message)s')
logging.error('this is a message\ndfdf')