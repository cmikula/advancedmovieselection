#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  Coded by cmikula (c)2016
#  Support: www.i-have-a-dreambox.com
#
#  This plugin is licensed under the Creative Commons 
#  Attribution-NonCommercial-ShareAlike 3.0 Unported 
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter to Creative
#  Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#  Alternatively, this plugin may be distributed and executed on hardware which
#  is licensed by Dream Multimedia GmbH.
#
#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially 
#  distributed other than under the conditions noted above.
#

from threading import Thread, Event
from ServiceDescriptor import DirectoryEvent
from EventInformationTable import printStackTrace
from twisted.internet import reactor

class MovieCache():
    def __init__(self):
        self.__callback = []
        self.cacheUpdates = []
        self.pathInfoCache = dict()
        self.thread = Thread(target=self.__threadRun, name="AMS-CacheThread")
        self.event = Event()
        self.__run = True
        self.thread.start()
    
    def __threadRun(self):
        try:
            while self.__run:
                if len(self.cacheUpdates) == 0:
                    reactor.callFromThread(self.__notify) #@UndefinedVariable
                    self.event.wait()
                self.event.clear()
                print "[AdvancedMovieSelection] cache update"
                if len(self.cacheUpdates) == 0:
                    continue
                serviceref = self.cacheUpdates.pop()
                path = serviceref.getPath()
                print path
                de = DirectoryEvent(serviceref)
                de.scanFolder()
                de.updateFolderSize()
                self.pathInfoCache[path] = de
        except:
            printStackTrace()
        print "[AdvancedMovieSelection] cache thread finished"
        
    def destroy(self):
        self.__callback = []
        self.__run = False
        self.event.set()

    def addCallback(self, callback):
        if not callback in self.__callback:
            self.__callback.append(callback)

    def removeCallback(self, callback):
        if callback in self.__callback:
            self.__callback.remove(callback)
        
    def addService(self, serviceref):
        if not serviceref in self.cacheUpdates:
            self.cacheUpdates.append(serviceref)
            self.event.set()

    def updateItem(self, serviceref):
        if serviceref is not None:
            self.addService(serviceref)
        #path = serviceref.getPath()
        #if path in self.pathInfoCache:
        #    del self.pathInfoCache[path]

    def getItem(self, serviceref):
        path = serviceref.getPath()
        if self.pathInfoCache.has_key(path):
            return self.pathInfoCache[path]
        self.addService(serviceref)

    def __notify(self):
        for callback in self.__callback:
            callback()

        