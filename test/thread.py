# -*- coding: utf-8 -*-
import threading
import time

mylock = threading.RLock()
count = 0

class test(threading.Thread):

    def __init__(self, no, interval):
        threading.Thread.__init__(self)
        self.no = no
        self.interval = interval
        self.isstop = False

    def run(self):
        global count
        a = 0
        while not self.isstop:
            mylock.acquire()
            count += 1
            mylock.release()
            print 'thread %d = %d' % (self.no, count)
            time.sleep(self.interval)

    def stop(self):
        self.isstop = True


def factory():
    t1 = test(1, 1)
    t1.start()


    time.sleep(20)
    t1.stop()


if __name__ == '__main__':
    factory()