import os
from TMDb.tmdbapi import CONNECTION_TIMEOUT

REQUESTS = False
try:
    import requests #@UnresolvedImport
    REQUESTS = True
except:
    import json
    import urllib2

#from ..StopWatch import clockit

#@clockit
def downloadCover(url, filename, overwrite=False):
    try:
        if not url:
            return False
        if (not os.path.exists(filename) or overwrite) and url:
            #print "Try loading: ", str(url), "->", str(filename)
            if REQUESTS:
                print "request", str(url)
                r = requests.get(url, timeout=CONNECTION_TIMEOUT, stream=True)
                with open(filename, 'wb') as f:
                    f.write(r.content)
            else:
                print "urlopen", str(url)
                req = urllib2.Request(url=url)
                r = urllib2.urlopen(req, timeout=CONNECTION_TIMEOUT)
                with open(filename, 'wb') as f:
                    f.write(r.read())
        else:
            pass
            #print "Download skipped:", str(url), "->", str(filename)
    except:
        import sys, traceback
        print '-' * 50
        traceback.print_exc(file=sys.stdout)
        print '-' * 50
        return False
    return True
