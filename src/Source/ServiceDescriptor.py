#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  Coded by cmikula (c)2012
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

import os
from LocaleInit import _
from ServiceUtils import diskUsage, getDirSize, realSize
from Globals import printStackTrace
from Config import config
from StopWatch import clockit
from ServiceProvider import eServiceReferenceListAll
from MovieScanner import movieScanner

class DirectoryInfo():
    def __init__(self, dir_path):
        if dir_path and dir_path[-1] != '/':
            dir_path += '/'
        self.dir_path = dir_path
        self.meta_file = dir_path + ".meta"
        self.name = os.path.split(os.path.dirname(dir_path))[1]
        self.sort_type = 0
        self.used = 0
        self.dir_size = 0
        self.dir_count = 0
        self.mov_count = 0
        self.mov_seen = 0
        if dir_path != '/':
            self.__read(dir_path)
    
    def __parse_int(self, metafile):
        try:
            entry = metafile.readline().rstrip()
            if entry is not None:
                return int(entry)
        except:
            pass
        return -1

    def __read(self, dir_path):
        try:
            if os.path.exists(self.meta_file):
                metafile = open(self.meta_file, "r")
                self.name = metafile.readline().rstrip()
                self.sort_type = self.__parse_int(metafile)
                self.used = self.__parse_int(metafile)
                self.dir_size = self.__parse_int(metafile)
                self.dir_count = self.__parse_int(metafile)
                self.mov_count = self.__parse_int(metafile)
                #self.rest = metafile.read()
                metafile.close()
        except:
            printStackTrace()

    def write(self):
        if self.meta_file == '/.meta':
            print "[AdvancedMovieSelection] Write new meta skipped"
            return
        metafile = None
        try:
            print "[AdvancedMovieSelection] Write new meta:", self.meta_file, self.sort_type, self.used
            metafile = open(self.meta_file, "w")
            metafile.write(str(self.name) + '\n')
            metafile.write(str(self.sort_type) + '\n')
            #metafile.write(str(self.used) + '\n')
            #metafile.write(str(self.dir_size) + '\n')
            #metafile.write(str(self.dir_count) + '\n')
            #metafile.write(str(self.mov_count) + '\n')
            metafile.close()
        except:
            printStackTrace()
            if metafile is not None:
                metafile.close()

    
    def setSortType(self, sort_type):
        self.sort_type = sort_type
    
    def setName(self, name):
        self.name = name

    def isDiskSpaceChanged(self, update=True):
        total, used, free = diskUsage(self.dir_path)
        result = self.used != used
        if result and update:
            print "[AdvancedMovieSelection] update disc usage:", total, self.used, used, free
            self.used = used
        return result

    def updateFolderSize(self):
        self.dir_size = getDirSize(self.dir_path)
        #print "scanned folder size", self.dir_size
    
    def scanFolder(self):
        i = movieScanner.scanForMovies(self.dir_path, False)
        self.mov_count = len(i[0])
        self.mov_seen = i[2]
        self.dir_count = 0
        self.dir_size = i[1]
    
    def getmount(self, path=None):
        path = path and path or self.dir_path
        path = os.path.abspath(path)
        while path != os.path.sep:
            if os.path.ismount(path):
                return path
            path = os.path.abspath(os.path.join(path, os.pardir))
        if path == '/':
            return None
        return path
    
    def updateDiskUsage(self, dir_count=None, movie_count=None):
        #mount = self.getmount()
        #if not mount:
        #    return
        try:
            if self.isDiskSpaceChanged():
                self.updateFolderSize()
                if dir_count is not None:
                    self.dir_count = dir_count
                if movie_count is not None:
                    self.mov_count = movie_count
                #self.write()
        except:
            printStackTrace()
        # update disk usage on mount directory
        #di = DirectoryInfo(mount)
        #if di.isDiskSpaceChanged():
        #    di.updateFolderSize()
        #    di.write()

class DirectoryEvent(DirectoryInfo):
    def __init__(self, serviceref):
        DirectoryInfo.__init__(self, serviceref.getPath())
        self.is_movielibrary = False
        dbinfo = None
        if isinstance(serviceref, eServiceReferenceListAll):
            dbinfo = movieScanner.movielibrary.getFullCount()
            self.is_movielibrary = True
        if dbinfo is not None:
            self.mov_count = dbinfo[0]
            self.mov_seen = dbinfo[1]
            self.dir_count = dbinfo[2]
            self.dir_size = dbinfo[3]

    def getEventName(self):
        return self.name
    
    def getShortDescription(self):
        return self.dir_path

    def getDBDescription(self):
        text1 = []
        
        if self.dir_size > 0:
            text1.append(realSize(self.dir_size, 3))
        if self.dir_count > 0:
            text1.append(str(self.dir_count) + ' ' + _("Directories"))
        if self.mov_count > 0:
            text1.append(str(self.mov_count) + ' ' + _("Movies"))
            text1.append(str(self.mov_seen) + ' ' + _("seen"))
            text1.append(str(self.mov_count - self.mov_seen) + ' ' + _("new"))
        
        result = ", ".join(text1)
        if movieScanner.last_update:
            result += "\r\n" + _("Last update:") + ' ' + movieScanner.getLastUpdate()
        
        return result

    def getDirDescription(self):
        text = _("Name:") + ' ' + self.name
        text1 = []
        if self.dir_size > 0:
            text1.append(realSize(self.dir_size, 3))
        if self.dir_count > 0:
            text1.append(str(self.dir_count) + ' ' + _("Directories"))
        if self.mov_count > 0:
            text1.append(str(self.mov_count) + ' ' + _("Movies"))
            text1.append(str(self.mov_seen) + ' ' + _("seen"))
            text1.append(str(self.mov_count - self.mov_seen) + ' ' + _("new"))

        if len(text1) > 0:
            text += "  (" + ", ".join(text1) + ")"
        text = [text]

        #mount_path = self.getmount()
        # TODO temporary disabled, performance issue on mass storage devices
        if config.AdvancedMovieSelection.show_diskusage.value and os.path.exists(self.dir_path):
            total, used, free = diskUsage(self.dir_path)
            #text.append(_("Media:") + ' ' + str(mount_path))
            text.append(_("Total:") + ' ' + realSize(total, 3))
            text.append(_("Used:") + ' ' + realSize(used, 3))
            text.append(_("Free:") + ' ' + realSize(free, 3))
            real_path = os.path.realpath(self.dir_path) + os.sep
            if self.dir_path != real_path:
                text.append(_("Symlink:") + ' ' + real_path)
        
        return "\n".join(text)
    
    @clockit
    def getExtendedDescription(self):
        if not self.is_movielibrary:
            return self.getDirDescription()
        else:
            return self.getDBDescription()

    def getEventId(self):
        return 0

    def getBeginTimeString(self):
        return ""
    
    def getDuration(self):
        return 0
    
    def getBeginTime(self):
        return 0
    
    def getComponentData(self):
        return ""
    
