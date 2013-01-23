import os, urllib
from ..StopWatch import clockit

@clockit
def downloadCover(url, filename):
    try:
        if not os.path.exists(filename):
            print "Try loading: ", str(url), "->", str(filename)
            urllib.urlretrieve(url, filename)
    except:
        import sys, traceback
        print '-' * 50
        traceback.print_exc(file=sys.stdout)
        print '-' * 50
        return False
    return True
