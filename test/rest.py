# -*- coding: utf-8 -*-
from restkit import request
import timeit
def readurl():
    r = request('http://friendpaste.com/1ZSEoJeOarc3ULexzWOk5Y_633433316631/raw')
    print "RESULT: %s: %s (%s)" % (u, r.status, len(r.body_string()))


# t = timeit.Timer(stmt=extract)
# print "%.2f s" % t.timeit(number=1)