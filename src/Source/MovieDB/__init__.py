import os, urllib
#from ..StopWatch import clockit

#@clockit
def downloadCover(url, filename, overwrite=False):
    try:
        if not url:
            return False
        if (not os.path.exists(filename) or overwrite) and url:
            #print "Try loading: ", str(url), "->", str(filename)
            urllib.urlretrieve(url, filename)
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
