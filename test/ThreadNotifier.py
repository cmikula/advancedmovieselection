import threading
class ThreadNotifier():
    def __init__(self):
        from timer import eTimer
        self.count = 0
        self.__showThreadsTimer = eTimer()
        self.__showThreadsTimer.callback.append(self.__showThreads)
        self.__showThreadsTimer.start(1000, False)
    
    def __showThreads(self):
        tcount = threading.activeCount()
        if self.count != tcount:
            self.count = tcount
            print "#" * 80
            print "Threads: {0}".format(tcount)
            for t in threading.enumerate():
                print "{0} {1} {2}".format(t, t.isAlive(), t.isDaemon())
            print "#" * 80
tn = ThreadNotifier()
