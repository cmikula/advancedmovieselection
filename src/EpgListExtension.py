#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Copyright (C) 2012 cmikula

In case of reuse of this source code please do not remove this copyright.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    For more information on the GNU General Public License see:
    <http://www.gnu.org/licenses/>.

For example, if you distribute copies of such a program, whether gratis or for a fee, you 
must pass on to the recipients the same freedoms that you received. You must make sure 
that they, too, receive or can get the source code. And you must show them these terms so they know their rights.
'''

from Components.EpgList import EPGList
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, SCOPE_CURRENT_PLUGIN

IMAGE_PATH = "Extensions/AdvancedMovieSelection/images/"
av_pixmap = LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + "movie.png"))

savedPixmapForEntry = EPGList.getPixmapForEntry
savedBuildSingleEntry = EPGList.buildSingleEntry
savedBuildMultiEntry = EPGList.buildMultiEntry
savedBuildSimilarEntry = EPGList.buildSimilarEntry

def getPixmapForEntry(self, service, eventId, beginTime, duration):
    pixmap = savedPixmapForEntry(self, service, eventId, beginTime, duration)
    if pixmap[0] == None and epgListExtension.isMovieRecorded():
        return (av_pixmap, 1)
    return pixmap

def buildSingleEntry(self, service, eventId, beginTime, duration, EventName):
    epgListExtension.current_name = EventName
    return savedBuildSingleEntry(self, service, eventId, beginTime, duration, EventName)

def buildMultiEntry(self, changecount, service, eventId, beginTime, duration, EventName, nowTime, service_name):
    epgListExtension.current_name = EventName
    return savedBuildMultiEntry(self, changecount, service, eventId, beginTime, duration, EventName, nowTime, service_name)

def buildSimilarEntry(self, service, eventId, beginTime, service_name, duration):
    return savedBuildSimilarEntry(self, service, eventId, beginTime, service_name, duration)

class EPGListExtension():
    def __init__(self):
        self.current_name = ""
        self.recorded_movies = []
        self.isWorking = False
    
    def enabled(self, enabled):
        print "[AdvancedMovieSelection] Set epg extension:", str(enabled)
        if enabled:
            EPGList.getPixmapForEntry = getPixmapForEntry
            EPGList.buildSingleEntry = buildSingleEntry
            EPGList.buildMultiEntry = buildMultiEntry
            #EPGList.buildSimilarEntry = buildSimilarEntry
            self.reloadMoviesAsync()
        else:
            EPGList.getPixmapForEntry = savedPixmapForEntry
            EPGList.buildSingleEntry = savedBuildSingleEntry
            EPGList.buildMultiEntry = savedBuildMultiEntry
            #EPGList.buildSimilarEntry = savedBuildSimilarEntry
            
    def isMovieRecorded(self):
        return self.recorded_movies.__contains__(self.current_name)
    
    def reloadMoviesAsync(self, search_path="/media/"):
        if self.isWorking:
            print "[AdvancedMovieSelection] EPGListExtension reload is working"
            return
        from thread import start_new_thread
        start_new_thread(self.updateMovieList, (search_path,))
    
    def updateMovieList(self, search_path):
        try:
            self.isWorking = True
            print "[AdvancedMovieSelection] Start update recorded movies in location", search_path[0]
            import os
            from Trashcan import TRASH_EXCLUDE
            self.recorded_movies = []
            for (path, dirs, files) in os.walk(search_path[0]):
                # Skip excluded directories here
                sp = path.split("/")
                if len(sp) > 2:
                    if sp[2] in TRASH_EXCLUDE:
                        continue
                         
                for filename in files:
                    if filename.endswith(".ts"):
                        meta_path = os.path.join(path, filename + ".meta")
                        if os.path.exists(meta_path):
                            f = open(meta_path, "r")
                            f.readline()
                            name = f.readline().rstrip("\r\n")
                            f.close()
                            #print "[AdvancedMovieSelection] Add movie per name:", name
                            self.recorded_movies.append(name)
        except Exception, e:
            print e
        self.isWorking = False
        print "[AdvancedMovieSelection] Finished update recorded movies"

epgListExtension = EPGListExtension()
