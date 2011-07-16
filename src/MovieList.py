#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  The plugin is developed on the basis from a lot of single plugins (thx for the code @ all)
#  Coded by JackDaniel (c)2011
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
from __init__ import _
from Components.GUIComponent import GUIComponent
from Tools.FuzzyDate import FuzzyTime
from ServiceReference import ServiceReference
from Components.MultiContent import MultiContentEntryText, MultiContentEntryProgress
from Components.config import config
from enigma import eListboxPythonMultiContent, eListbox, gFont, iServiceInformation, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, eServiceReference
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, SCOPE_CURRENT_PLUGIN
import os
from skin import parseColor
import NavigationInstance
from timer import TimerEntry
from stat import ST_MTIME as stat_ST_MTIME
from time import time as time_time
from math import fabs as math_fabs
from datetime import datetime
from ServiceProvider import detectDVDStructure, getCutList, Info, ServiceCenter, eServiceReferenceDvd
from os import environ

IMAGE_PATH = "Extensions/AdvancedMovieSelection/images/"

MEDIAEXTENSIONS = {
        "ts": "movie",
        "iso": "movie",
        "avi": "movie",
        "divx": "movie",
        "mpg": "movie",
        "mpeg": "movie",
        "mkv": "movie",
        "mp4": "movie",
        "m4v": "movie",
        "flv": "movie",
        "m2ts": "movie",
        "mov": "movie"
    }

class MovieList(GUIComponent):
    SORT_ALPHANUMERIC = 1
    SORT_RECORDED = 2

    SORT_DATE_ASC = 3
    SORT_DATE_DESC = 4

    LISTTYPE_ORIGINAL = 1
    LISTTYPE_COMPACT_DESCRIPTION = 2
    LISTTYPE_COMPACT = 3
    LISTTYPE_MINIMAL = 4
    LISTTYPE_MINIMAL_AdvancedMovieSelection = 5

    HIDE_DESCRIPTION = 1
    SHOW_DESCRIPTION = 2
    HIDE_DATE = 1
    SHOW_DATE = 2
    HIDE_TIME = 1
    SHOW_TIME = 2
    HIDE_SERVICE = 1
    SHOW_SERVICE = 2

    def __init__(self, root, list_type=None, sort_type=None, descr_state=None, show_folders=False, show_progressbar=False, show_statusicon=False, show_statuscolor=False, show_date=True, show_time=True, show_service=True):
        GUIComponent.__init__(self)
        self.list_type = list_type or self.LISTTYPE_ORIGINAL
        self.descr_state = descr_state or self.HIDE_DESCRIPTION
        self.sort_type = sort_type or self.SORT_DATE_ASC
        self.sort_type = sort_type or self.SORT_DATE_DESC
        self.show_folders = show_folders
        self.show_progressbar = show_progressbar
        self.show_statusicon = show_statusicon
        self.show_statuscolor = show_statuscolor
        self.show_date = show_date or self.HIDE_DATE
        self.show_date = show_date or self.SHOW_DATE
        self.show_time = show_time or self.HIDE_TIME
        self.show_time = show_time or self.SHOW_TIME
        self.show_service = show_service or self.HIDE_SERVICE
        self.show_service = show_service or self.SHOW_SERVICE
        self.l = eListboxPythonMultiContent()
        self.tags = set()
        
        if root is not None:
            self.reload(root)
        
        self.redrawList()
        self.l.setBuildFunc(self.buildMovieListEntry)
        
        self.onSelectionChanged = [ ]

        if config.AdvancedMovieSelection.color1.value == "yellow":
            newcolor1 = 0xffcc00
        if config.AdvancedMovieSelection.color1.value == "blue":
            newcolor1 = 0x8585ff
        if config.AdvancedMovieSelection.color1.value == "red":
            newcolor1 = 0xff4A3C
        if config.AdvancedMovieSelection.color1.value == "black":
            newcolor1 = 0x000000
        if config.AdvancedMovieSelection.color1.value == "green":
            newcolor1 = 0x38FF48           
        if config.AdvancedMovieSelection.color2.value == "yellow":
            newcolor2 = 0xffcc00
        if config.AdvancedMovieSelection.color2.value == "blue":
            newcolor2 = 0x8585ff
        if config.AdvancedMovieSelection.color2.value == "red":
            newcolor2 = 0xff4A3C
        if config.AdvancedMovieSelection.color2.value == "black":
            newcolor2 = 0x000000
        if config.AdvancedMovieSelection.color2.value == "green":
            newcolor2 = 0x38FF48                  
        if config.AdvancedMovieSelection.color3.value == "yellow":
            newcolor3 = 0xffcc00
        if config.AdvancedMovieSelection.color3.value == "blue":
            newcolor3 = 0x8585ff
        if config.AdvancedMovieSelection.color3.value == "red":
            newcolor3 = 0xff4A3C
        if config.AdvancedMovieSelection.color3.value == "black":
            newcolor3 = 0x000000
        if config.AdvancedMovieSelection.color3.value == "green":
            newcolor3 = 0x38FF48    

        try: self.watching_color = parseColor("movieWatching").argb()    
        except: self.watching_color = newcolor1
        try: self.finished_color = parseColor("movieFinished").argb()    
        except: self.finished_color = newcolor2
        try: self.recording_color = parseColor("movieRecording").argb()    
        except: self.recording_color = newcolor3

    def connectSelChanged(self, fnc):
        if not fnc in self.onSelectionChanged:
            self.onSelectionChanged.append(fnc)

    def disconnectSelChanged(self, fnc):
        if fnc in self.onSelectionChanged:
            self.onSelectionChanged.remove(fnc)

    def selectionChanged(self):
        for x in self.onSelectionChanged:
            x()

    def setListType(self, type):
        self.list_type = type

    def setDescriptionState(self, val):
        self.descr_state = val

    def setSortType(self, type):
        self.sort_type = type

    def showFolders(self, val):
        self.show_folders = val

    def showProgressbar(self, val):
        self.show_progressbar = val

    def showStatusIcon(self, val):
        self.show_statusicon = val

    def showStatusColor(self, val):
        self.show_statuscolor = val
        
    def showDate(self, val):
        self.show_date = val
        
    def showTime(self, val):
        self.show_time = val
        
    def showService(self, val):
        self.show_service = val

    def redrawList(self):
        if self.list_type == MovieList.LISTTYPE_ORIGINAL:
            self.l.setFont(0, gFont("Regular", 22))
            self.l.setFont(1, gFont("Regular", 19))
            self.l.setFont(2, gFont("Regular", 16))
            self.l.setItemHeight(78)
        elif self.list_type == MovieList.LISTTYPE_COMPACT_DESCRIPTION or self.list_type == MovieList.LISTTYPE_COMPACT:
            self.l.setFont(0, gFont("Regular", 20))
            self.l.setFont(1, gFont("Regular", 14))
            self.l.setItemHeight(39)
        else:
            if self.list_type == MovieList.LISTTYPE_MINIMAL_AdvancedMovieSelection:
                self.l.setFont(0, gFont("Regular", 18))
                self.l.setItemHeight(26)
            else:
                self.l.setFont(0, gFont("Regular", 20))
                self.l.setFont(1, gFont("Regular", 16))
                self.l.setItemHeight(26)

    def buildMovieListEntry(self, serviceref, info, begin, len):
        width = self.l.getItemSize().width()
        if self.show_folders:
            if serviceref.flags & eServiceReference.mustDescent:
                res = [ None ]
                png = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + "directory.png"))
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 0, 2, 20, 20, png))
                res.append(MultiContentEntryText(pos=(25, 0), size=(width - 40, 30), font=0, flags=RT_HALIGN_LEFT, text=serviceref.getName()))
                return res
            extension = serviceref.toString().split('.')
            extension = extension[-1].lower()
            offset = 25
            if MEDIAEXTENSIONS.has_key(extension):
                filename = os.path.realpath(serviceref.getPath())
                if os.path.exists("%s.gm" % filename) and config.AdvancedMovieSelection.shownew.value:
                    if environ["LANGUAGE"] == "de":                    
                        png = LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + "movie_de_new.png"))
                    elif environ["LANGUAGE"] == "de_DE":                    
                        png = LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + "movie_de_new.png"))
                    elif environ["LANGUAGE"] == "en":
                        png = LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + "movie_en_new.png"))
                    else:
                        png = LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + "movie_new.png"))
                else:
                    png = LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + MEDIAEXTENSIONS[extension] + ".png"))
            else:
                if isinstance(serviceref, eServiceReferenceDvd):
                    png = LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + "dvd_watching.png"))
                else:
                    png = None
        else:
            if serviceref.flags & eServiceReference.mustDescent:
                return None
            offset = 0

        if info is not None:
            if len <= 0: #recalc len when not already done
                cur_idx = self.l.getCurrentSelectionIndex()
                x = self.list[cur_idx]
                if config.usage.load_length_of_movies_in_moviellist.value:
                    len = x[1].getLength(x[0]) #recalc the movie length...
                else:
                    len = 0 #dont recalc movielist to speedup loading the list
                self.list[cur_idx] = (x[0], x[1], x[2], len) #update entry in list... so next time we don't need to recalc

        length = len
    
        if len > 0:
            len = "%d:%02d" % (len / 60, len % 60)
        else:
            len = ""
        
        res = [ None ]
        if info is not None:
            txt = info.getName(serviceref)
            if not isinstance(info, Info):
                service = ServiceReference(info.getInfoString(serviceref, iServiceInformation.sServiceref))
            else:
                service = info.getServiceReference()
            description = info.getInfoString(serviceref, iServiceInformation.sDescription)
            tags = info.getInfoString(serviceref, iServiceInformation.sTags)

        color = None 
        recording = False
        if NavigationInstance.instance.getRecordings():
            for timer in NavigationInstance.instance.RecordTimer.timer_list:
                if timer.state == TimerEntry.StateRunning:
                    try:
                        filename = "%s.ts" % timer.Filename
                    except:
                        filename = ""
                    if filename and os.path.realpath(filename) == os.path.realpath(serviceref.getPath()):
                        recording = True
                        break
        if not recording:
            filename = os.path.realpath(serviceref.getPath())
            if os.path.exists("%s.sc" % filename) and not os.path.exists("%s.ap" % filename):
                # double check, sometimes ap file was not created (e.g. after enigma2 crash)
                filestats = os.stat(filename)
                currentTime = time_time()
                mtime = filestats[stat_ST_MTIME]
                if math_fabs(mtime - int(currentTime)) <= 10:
                    recording = True
        if recording and self.show_statuscolor:
            color = self.recording_color

        if self.show_statusicon and self.show_folders and config.AdvancedMovieSelection.color3.value == "yellow" and recording:
            png = LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + "yellow_movieicon.png"))
        if self.show_statusicon and self.show_folders and config.AdvancedMovieSelection.color3.value == "blue" and recording:
            png = LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + "blue_movieicon.png"))
        if self.show_statusicon and self.show_folders and config.AdvancedMovieSelection.color3.value == "red" and recording:
            png = LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + "red_movieicon.png"))
        if self.show_statusicon and self.show_folders and config.AdvancedMovieSelection.color3.value == "black" and recording:
            png = LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + "black_movieicon.png"))
        if self.show_statusicon and self.show_folders and config.AdvancedMovieSelection.color3.value == "green" and recording:
            png = LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + "green_movieicon.png"))

        if self.show_progressbar or (self.show_statusicon and self.show_folders) or self.show_statuscolor:
            last = None
            if length <= 0: #Set default file length if is not calculateable
                length = 5400
            cue = None #info.cueSheet()
            if cue is None:
                cut_list = getCutList(serviceref.getPath())
                for (pts, what) in cut_list:
                    if what == 1 and length == 5400:
                        length = pts / 90000
                    if what == 3:
                        last = pts
            elif cue is not None:
                cut_list = cue.getCutList()
                for (pts, what) in cut_list:
                    if what == 1 and length == 5400:
                        length = pts / 90000
                    if what == 3:
                        last = pts
            perc = 0
            if last is not None and length > 0:
                perc = int((float(last) / 90000 / float(length)) * 100);
                if self.show_statuscolor and not recording:
                    if (perc > 1) and (perc <= config.AdvancedMovieSelection.moviepercentseen.value):
                        color = self.watching_color
                    elif (perc > config.AdvancedMovieSelection.moviepercentseen.value):
                        color = self.finished_color
                if self.show_statusicon and self.show_folders and not recording:
                    if (perc > 1) and (perc <= config.AdvancedMovieSelection.moviepercentseen.value) and config.AdvancedMovieSelection.color1.value == "yellow":
                        png = LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + "yellow_movieicon.png"))
                    if (perc > 1) and (perc <= config.AdvancedMovieSelection.moviepercentseen.value) and config.AdvancedMovieSelection.color1.value == "blue":
                        png = LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + "blue_movieicon.png"))
                    if (perc > 1) and (perc <= config.AdvancedMovieSelection.moviepercentseen.value) and config.AdvancedMovieSelection.color1.value == "red":
                        png = LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + "red_movieicon.png"))
                    if (perc > 1) and (perc <= config.AdvancedMovieSelection.moviepercentseen.value) and config.AdvancedMovieSelection.color1.value == "black":
                        png = LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + "black_movieicon.png"))
                    if (perc > 1) and (perc <= config.AdvancedMovieSelection.moviepercentseen.value) and config.AdvancedMovieSelection.color1.value == "green":
                        png = LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + "green_movieicon.png"))
                    elif (perc > config.AdvancedMovieSelection.moviepercentseen.value) and config.AdvancedMovieSelection.color2.value == "yellow":
                        png = LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + "yellow_movieicon.png"))
                    elif (perc > config.AdvancedMovieSelection.moviepercentseen.value) and config.AdvancedMovieSelection.color2.value == "blue":
                        png = LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + "blue_movieicon.png"))
                    elif (perc > config.AdvancedMovieSelection.moviepercentseen.value) and config.AdvancedMovieSelection.color2.value == "red":
                        png = LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + "red_movieicon.png"))
                    elif (perc > config.AdvancedMovieSelection.moviepercentseen.value) and config.AdvancedMovieSelection.color2.value == "black":
                        png = LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + "black_movieicon.png"))
                    elif (perc > config.AdvancedMovieSelection.moviepercentseen.value) and config.AdvancedMovieSelection.color2.value == "green":
                        png = LoadPixmap(resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + "green_movieicon.png"))
                if perc > 100:
                    perc = 100
                if perc < 0:
                    perc = 0
            if self.show_progressbar:
                top = int((self.l.getItemSize().height() - 6) / 2) + 1
                res.append(MultiContentEntryProgress(pos=(0 + offset, top), size=(50, 6), percent=perc, borderWidth=1, foreColor=color))
                offset = offset + 55

        begin_string = ""
        if recording:
            if config.AdvancedMovieSelection.dateformat.value == "6":
                begin_string = (_("REC"))
            else:
                if config.AdvancedMovieSelection.dateformat.value == "7":
                    begin_string = (_("REC"))
                else:
                    begin_string = (_("Records"))        
        else:
            if config.AdvancedMovieSelection.dateformat.value == "2" and begin > 0:
            #if begin > 0:
                t = FuzzyTime(begin)
                begin_string = t[0] + ", " + t[1]
            elif config.AdvancedMovieSelection.dateformat.value == "1":
                d = datetime.fromtimestamp(begin)
                begin_string = d.strftime("%d.%m.%Y")
            elif config.AdvancedMovieSelection.dateformat.value == "3":
                d = datetime.fromtimestamp(begin)
                begin_string = d.strftime("%d.%m.%Y - %H:%M")
            elif config.AdvancedMovieSelection.dateformat.value == "4":
                d = datetime.fromtimestamp(begin)
                begin_string = d.strftime("%m.%d.%Y")
            elif config.AdvancedMovieSelection.dateformat.value == "5":
                d = datetime.fromtimestamp(begin)
                begin_string = d.strftime("%m.%d.%Y - %H:%M")
            elif config.AdvancedMovieSelection.dateformat.value == "6":
                d = datetime.fromtimestamp(begin)
                begin_string = d.strftime("%d.%m")
            elif config.AdvancedMovieSelection.dateformat.value == "7":
                d = datetime.fromtimestamp(begin)
                begin_string = d.strftime("%m.%d")

        if self.list_type == MovieList.LISTTYPE_ORIGINAL:
            if self.show_folders:
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 0, 29, 20, 20, png))
            res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 265, 30), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
            if self.tags:
                res.append(MultiContentEntryText(pos=(width - 180, 0), size=(180, 30), font=2, flags=RT_HALIGN_RIGHT, text=tags, color=color))
                if service is not None:
                    res.append(MultiContentEntryText(pos=(300, 50), size=(200, 25), font=1, flags=RT_HALIGN_LEFT, text=service.getServiceName(), color=color))
            else:
                if service is not None:
                    res.append(MultiContentEntryText(pos=(width - 180, 0), size=(180, 30), font=2, flags=RT_HALIGN_RIGHT, text=service.getServiceName(), color=color))
                res.append(MultiContentEntryText(pos=(0 + offset, 28), size=(width, 25), font=1, flags=RT_HALIGN_LEFT, text=description, color=color))
            if self.show_date == MovieList.SHOW_DATE and self.show_time == MovieList.SHOW_TIME:
                res.append(MultiContentEntryText(pos=(0 + offset, 55), size=(200, 20), font=1, flags=RT_HALIGN_LEFT, text=begin_string, color=color))
                res.append(MultiContentEntryText(pos=(width - 200, 55), size=(198, 20), font=1, flags=RT_HALIGN_RIGHT, text=len, color=color))
            if self.show_date == MovieList.HIDE_DATE and self.show_time == MovieList.SHOW_TIME:
                res.append(MultiContentEntryText(pos=(width - 200, 55), size=(198, 20), font=1, flags=RT_HALIGN_RIGHT, text=len, color=color))
            if self.show_date == MovieList.SHOW_DATE and self.show_time == MovieList.HIDE_TIME:
                res.append(MultiContentEntryText(pos=(0 + offset, 55), size=(200, 20), font=1, flags=RT_HALIGN_LEFT, text=begin_string, color=color))

        elif self.list_type == MovieList.LISTTYPE_COMPACT_DESCRIPTION:
            if self.show_folders:
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 0, 9, 20, 20, png))
            res.append(MultiContentEntryText(pos=(0 + offset, 22), size=(width - 212, 17), font=1, flags=RT_HALIGN_LEFT, text=description, color=color))
            if self.show_date == MovieList.SHOW_DATE and config.AdvancedMovieSelection.dateformat.value == "1":
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 170, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 80, 4), size=(80, 20), font=1, flags=RT_HALIGN_RIGHT, text=begin_string, color=color))                            
            if self.show_date == MovieList.SHOW_DATE and config.AdvancedMovieSelection.dateformat.value == "2":
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 170, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 130, 4), size=(130, 20), font=1, flags=RT_HALIGN_RIGHT, text=begin_string, color=color))                            
            if self.show_date == MovieList.SHOW_DATE and config.AdvancedMovieSelection.dateformat.value == "3":
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 220, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 130, 4), size=(130, 20), font=1, flags=RT_HALIGN_RIGHT, text=begin_string, color=color))                
            if self.show_date == MovieList.SHOW_DATE and config.AdvancedMovieSelection.dateformat.value == "4":
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 170, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 80, 4), size=(80, 20), font=1, flags=RT_HALIGN_RIGHT, text=begin_string, color=color))                
            if self.show_date == MovieList.SHOW_DATE and config.AdvancedMovieSelection.dateformat.value == "5":
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 220, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 130, 4), size=(130, 20), font=1, flags=RT_HALIGN_RIGHT, text=begin_string, color=color))                
            if self.show_date == MovieList.SHOW_DATE and config.AdvancedMovieSelection.dateformat.value == "6":
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 130, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 40, 4), size=(40, 20), font=1, flags=RT_HALIGN_RIGHT, text=begin_string, color=color))                
            if self.show_date == MovieList.SHOW_DATE and config.AdvancedMovieSelection.dateformat.value == "7":
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 130, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 40, 4), size=(40, 20), font=1, flags=RT_HALIGN_RIGHT, text=begin_string, color=color))            
            if self.show_date == MovieList.HIDE_DATE:
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 0, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))                
            if service is not None and self.show_time == MovieList.SHOW_TIME:
                res.append(MultiContentEntryText(pos=(width - 205, 22), size=(154, 17), font=1, flags=RT_HALIGN_RIGHT, text=service.getServiceName(), color=color))
                res.append(MultiContentEntryText(pos=(width - 45, 22), size=(45, 20), font=1, flags=RT_HALIGN_RIGHT, text=len, color=color))            
            if service is not None and self.show_time == MovieList.HIDE_TIME:
                res.append(MultiContentEntryText(pos=(width - 154, 22), size=(154, 17), font=1, flags=RT_HALIGN_RIGHT, text=service.getServiceName(), color=color))

        elif self.list_type == MovieList.LISTTYPE_COMPACT:
            if self.show_folders:
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 0, 9, 20, 20, png))            
            if self.show_date == MovieList.SHOW_DATE and self.show_time == MovieList.HIDE_TIME:
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 77, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(0 + offset, 22), size=(200, 17), font=1, flags=RT_HALIGN_LEFT, text=begin_string, color=color))            
            if self.show_date == MovieList.SHOW_DATE and self.show_time == MovieList.SHOW_TIME:
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 155, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(0 + offset, 22), size=(200, 17), font=1, flags=RT_HALIGN_LEFT, text=begin_string, color=color))
                res.append(MultiContentEntryText(pos=(width - 75, 0), size=(75, 20), font=0, flags=RT_HALIGN_RIGHT, text=len, color=color))            
            if self.show_date == MovieList.HIDE_DATE and self.show_time == MovieList.HIDE_TIME:
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 0, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))            
            if self.show_date == MovieList.HIDE_DATE and self.show_time == MovieList.SHOW_TIME:
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 155, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 75, 0), size=(75, 20), font=0, flags=RT_HALIGN_RIGHT, text=len, color=color))            
            if self.tags:
                res.append(MultiContentEntryText(pos=(width - 200, 22), size=(200, 17), font=1, flags=RT_HALIGN_RIGHT, text=tags, color=color))
                if service is not None:
                    res.append(MultiContentEntryText(pos=(200, 22), size=(200, 17), font=1, flags=RT_HALIGN_LEFT, text=service.getServiceName(), color=color))
            else:
                if service is not None:
                    res.append(MultiContentEntryText(pos=(width - 200, 22), size=(200, 17), font=1, flags=RT_HALIGN_RIGHT, text=service.getServiceName(), color=color))        

        elif self.list_type == MovieList.LISTTYPE_MINIMAL_AdvancedMovieSelection:
            if self.show_folders:
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 0, 3, 20, 20, png))
            if self.show_date == MovieList.SHOW_DATE:
                res.append(MultiContentEntryText(pos=(0 + offset, 2), size=(160, 20), font=0, flags=RT_HALIGN_LEFT, text=begin_string, color=color))
            else:
                res.append(MultiContentEntryText(pos=(0, 2), size=(0, 20), font=0, flags=RT_HALIGN_LEFT, color=color))
            offsetServiceName = 0
            if service is not None and self.show_service == MovieList.SHOW_SERVICE:
                servicename = str(service.getServiceName())
                res.append(MultiContentEntryText(pos=(width - 170, 2), size=(170, 20), font=0, flags=RT_HALIGN_RIGHT, text=servicename, color=color))
                if servicename:
                    offsetServiceName = 150

            displaytext = txt
            if description and self.show_date == MovieList.SHOW_DATE:
                displaytext = "- " + displaytext + " - " + description
            else:
                if description and self.show_date == MovieList.HIDE_DATE:
                    displaytext = displaytext + " - " + description
                else:
                    if self.show_date == MovieList.SHOW_DATE:
                        displaytext = "- " + displaytext
                    else:
                        displaytext = displaytext
                        
            if len and self.show_date == MovieList.SHOW_DATE and self.show_time == MovieList.SHOW_TIME:
                displaytext = displaytext + ' ' + "( " + len + " )"    
            elif len and self.show_date == MovieList.HIDE_DATE and self.show_time == MovieList.SHOW_TIME:
                displaytext = displaytext + ' ' + "( " + len + " )"

            if self.show_date == MovieList.SHOW_DATE and config.AdvancedMovieSelection.dateformat.value == "1":
                res.append(MultiContentEntryText(pos=(0 + offset + 100, 2), size=(width - (0 + offset + 100 + offsetServiceName) , 25), font=0, flags=RT_HALIGN_LEFT, text=displaytext, color=color))
            if self.show_date == MovieList.SHOW_DATE and config.AdvancedMovieSelection.dateformat.value == "2":
                res.append(MultiContentEntryText(pos=(0 + offset + 140, 2), size=(width - (0 + offset + 140 + offsetServiceName) , 25), font=0, flags=RT_HALIGN_LEFT, text=displaytext, color=color))
            if self.show_date == MovieList.SHOW_DATE and config.AdvancedMovieSelection.dateformat.value == "3":
                res.append(MultiContentEntryText(pos=(0 + offset + 165, 2), size=(width - (0 + offset + 165 + offsetServiceName) , 25), font=0, flags=RT_HALIGN_LEFT, text=displaytext, color=color))
            if self.show_date == MovieList.SHOW_DATE and config.AdvancedMovieSelection.dateformat.value == "4":
                res.append(MultiContentEntryText(pos=(0 + offset + 100, 2), size=(width - (0 + offset + 100 + offsetServiceName) , 25), font=0, flags=RT_HALIGN_LEFT, text=displaytext, color=color))
            if self.show_date == MovieList.SHOW_DATE and config.AdvancedMovieSelection.dateformat.value == "5":
                res.append(MultiContentEntryText(pos=(0 + offset + 165, 2), size=(width - (0 + offset + 165 + offsetServiceName) , 25), font=0, flags=RT_HALIGN_LEFT, text=displaytext, color=color))
            if self.show_date == MovieList.SHOW_DATE and config.AdvancedMovieSelection.dateformat.value == "6":
                res.append(MultiContentEntryText(pos=(0 + offset + 55, 2), size=(width - (0 + offset + 55 + offsetServiceName) , 25), font=0, flags=RT_HALIGN_LEFT, text=displaytext, color=color))            
            if self.show_date == MovieList.SHOW_DATE and config.AdvancedMovieSelection.dateformat.value == "7":
                res.append(MultiContentEntryText(pos=(0 + offset + 55, 2), size=(width - (0 + offset + 55 + offsetServiceName) , 25), font=0, flags=RT_HALIGN_LEFT, text=displaytext, color=color))            
            if self.show_date == MovieList.HIDE_DATE:
                res.append(MultiContentEntryText(pos=(0 + offset, 2), size=(width - (0 + offset + offsetServiceName) , 25), font=0, flags=RT_HALIGN_LEFT, text=displaytext, color=color))

        else:
            assert(self.list_type == MovieList.LISTTYPE_MINIMAL)
            if self.show_folders:
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 0, 3, 20, 20, png))
            
            if len:
                len2 = "- " + len
            
            if self.show_date == MovieList.SHOW_DATE and self.show_time == MovieList.SHOW_TIME and config.AdvancedMovieSelection.dateformat.value == "1":
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 235, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 145, 5), size=(80, 25), font=1, flags=RT_HALIGN_RIGHT, text=begin_string, color=color))
                res.append(MultiContentEntryText(pos=(width - 60, 5), size=(60, 25), font=1, flags=RT_HALIGN_RIGHT, text=len2, color=color))                                                     
            if self.show_date == MovieList.SHOW_DATE and self.show_time == MovieList.SHOW_TIME and config.AdvancedMovieSelection.dateformat.value == "2":
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 240, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 190, 5), size=(125, 25), font=1, flags=RT_HALIGN_RIGHT, text=begin_string, color=color))
                res.append(MultiContentEntryText(pos=(width - 60, 5), size=(60, 25), font=1, flags=RT_HALIGN_RIGHT, text=len2, color=color))                                                    
            if self.show_date == MovieList.SHOW_DATE and self.show_time == MovieList.SHOW_TIME and config.AdvancedMovieSelection.dateformat.value == "3":
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 295, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 205, 5), size=(140, 25), font=1, flags=RT_HALIGN_RIGHT, text=begin_string, color=color))
                res.append(MultiContentEntryText(pos=(width - 60, 5), size=(60, 25), font=1, flags=RT_HALIGN_RIGHT, text=len2, color=color))                           
            if self.show_date == MovieList.SHOW_DATE and self.show_time == MovieList.SHOW_TIME and config.AdvancedMovieSelection.dateformat.value == "4":
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 235, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 145, 5), size=(80, 25), font=1, flags=RT_HALIGN_RIGHT, text=begin_string, color=color))
                res.append(MultiContentEntryText(pos=(width - 60, 5), size=(60, 25), font=1, flags=RT_HALIGN_RIGHT, text=len2, color=color))                             
            if self.show_date == MovieList.SHOW_DATE and self.show_time == MovieList.SHOW_TIME and config.AdvancedMovieSelection.dateformat.value == "5":
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 295, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 205, 5), size=(140, 25), font=1, flags=RT_HALIGN_RIGHT, text=begin_string, color=color))
                res.append(MultiContentEntryText(pos=(width - 60, 5), size=(60, 25), font=1, flags=RT_HALIGN_RIGHT, text=len2, color=color))                          
            if self.show_date == MovieList.SHOW_DATE and self.show_time == MovieList.SHOW_TIME and config.AdvancedMovieSelection.dateformat.value == "6":
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 200, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 115, 5), size=(50, 25), font=1, flags=RT_HALIGN_RIGHT, text=begin_string, color=color))
                res.append(MultiContentEntryText(pos=(width - 60, 5), size=(60, 25), font=1, flags=RT_HALIGN_RIGHT, text=len2, color=color))                            
            if self.show_date == MovieList.SHOW_DATE and self.show_time == MovieList.SHOW_TIME and config.AdvancedMovieSelection.dateformat.value == "7":
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 200, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 115, 5), size=(50, 25), font=1, flags=RT_HALIGN_RIGHT, text=begin_string, color=color))
                res.append(MultiContentEntryText(pos=(width - 60, 5), size=(60, 25), font=1, flags=RT_HALIGN_RIGHT, text=len2, color=color))             
           
            if self.show_date == MovieList.SHOW_DATE and self.show_time == MovieList.HIDE_TIME and config.AdvancedMovieSelection.dateformat.value == "1":
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 175, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 90, 4), size=(90, 20), font=1, flags=RT_HALIGN_RIGHT, text=begin_string, color=color))                            
            if self.show_date == MovieList.SHOW_DATE and self.show_time == MovieList.HIDE_TIME and config.AdvancedMovieSelection.dateformat.value == "2":
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 175, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 90, 4), size=(90, 20), font=1, flags=RT_HALIGN_RIGHT, text=begin_string, color=color))                               
            if self.show_date == MovieList.SHOW_DATE and self.show_time == MovieList.HIDE_TIME and config.AdvancedMovieSelection.dateformat.value == "3":
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 230, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 150, 4), size=(150, 20), font=1, flags=RT_HALIGN_RIGHT, text=begin_string, color=color))                              
            if self.show_date == MovieList.SHOW_DATE and self.show_time == MovieList.HIDE_TIME and config.AdvancedMovieSelection.dateformat.value == "4":
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 175, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 90, 4), size=(90, 20), font=1, flags=RT_HALIGN_RIGHT, text=begin_string, color=color))                               
            if self.show_date == MovieList.SHOW_DATE and self.show_time == MovieList.HIDE_TIME and config.AdvancedMovieSelection.dateformat.value == "5":
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 230, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 150, 4), size=(150, 20), font=1, flags=RT_HALIGN_RIGHT, text=begin_string, color=color))              
            if self.show_date == MovieList.SHOW_DATE and self.show_time == MovieList.HIDE_TIME and config.AdvancedMovieSelection.dateformat.value == "6":
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 130, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 50, 4), size=(50, 20), font=1, flags=RT_HALIGN_RIGHT, text=begin_string, color=color))                            
            if self.show_date == MovieList.SHOW_DATE and self.show_time == MovieList.HIDE_TIME and config.AdvancedMovieSelection.dateformat.value == "7":
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 130, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 50, 4), size=(50, 20), font=1, flags=RT_HALIGN_RIGHT, text=begin_string, color=color))             
 
            if self.show_time == MovieList.SHOW_TIME and self.show_date == MovieList.HIDE_DATE:
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 150, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))
                res.append(MultiContentEntryText(pos=(width - 70, 2), size=(70, 20), font=0, flags=RT_HALIGN_RIGHT, text=len, color=color))                                    

            if self.show_date == MovieList.HIDE_DATE and self.show_time == MovieList.HIDE_TIME:
                res.append(MultiContentEntryText(pos=(0 + offset, 0), size=(width - 0, 25), font=0, flags=RT_HALIGN_LEFT, text=txt, color=color))

        return res

    def moveToIndex(self, index):
        self.instance.moveSelectionTo(index)

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()

    def getCurrentEvent(self):
        l = self.l.getCurrentSelection()
        return l and l[0] and l[1] and l[1].getEvent(l[0])

    def getCurrent(self):
        l = self.l.getCurrentSelection()
        return l and l[0]

    GUI_WIDGET = eListbox

    def postWidgetCreate(self, instance):
        instance.setContent(self.l)
        instance.selectionChanged.get().append(self.selectionChanged)

    def preWidgetRemove(self, instance):
        instance.setContent(None)
        instance.selectionChanged.get().remove(self.selectionChanged)

    def reload(self, root=None, filter_tags=None):
        if root is not None:
            self.load(root, filter_tags)
        else:
            self.load(self.root, filter_tags)
        self.l.setList(self.list)

    def removeService(self, service):
        for l in self.list[:]:
            if l[0] == service:
                self.list.remove(l)
        self.l.setList(self.list)

    def __len__(self):
        return len(self.list)

    def load(self, root, filter_tags):
        # this lists our root service, then building a 
        # nice list
        
        self.list = [ ]
        # cmi self.serviceHandler = eServiceCenter.getInstance()
        self.serviceHandler = ServiceCenter.getInstance()
        
        self.root = root
        list = self.serviceHandler.list(root)
        if list is None:
            print "listing of movies failed"
            list = [ ]    
            return
        tags = set()
        
        dirs = []

        while 1:
            serviceref = list.getNext()
            if not serviceref.valid():
                break
            dvd = None
            #dvd structure
            if serviceref.flags & eServiceReference.mustDescent:
                dvd = detectDVDStructure(serviceref.getPath())
                if dvd is not None:
                    serviceref = eServiceReferenceDvd(serviceref, True)
                    
            if dvd is None:
                if self.show_folders:
                    # Dr.Best: folder in movielist
                    if serviceref.flags & eServiceReference.mustDescent:
                        tempDir = serviceref.getPath()
                        parts = tempDir.split("/")
                        dirName = parts[-2]
                        serviceref.setName(dirName)
                        dirs.append((serviceref, None, -1, -1))
                        continue
                else:
                    if serviceref.flags & eServiceReference.mustDescent:
                        continue
        
            if serviceref.getPath().split(".")[-1].lower() == "iso":
                serviceref = eServiceReferenceDvd(serviceref)

            info = self.serviceHandler.info(serviceref)

            if dvd is not None:
                begin = long(os.stat(dvd).st_mtime)
            else:
                begin = info.getInfo(serviceref, iServiceInformation.sTimeCreate)

            # convert space-seperated list of tags into a set
            this_tags = info.getInfoString(serviceref, iServiceInformation.sTags).split(' ')
            if this_tags is None or this_tags == ['']:
                this_tags = []
            this_tags = set(this_tags)
            tags |= this_tags
        
            # filter_tags is either None (which means no filter at all), or 
            # a set. In this case, all elements of filter_tags must be present,
            # otherwise the entry will be dropped.            
            if filter_tags is not None and not this_tags.issuperset(filter_tags):
                continue
        
            self.list.append((serviceref, info, begin, -1))
        
        if self.sort_type == MovieList.SORT_ALPHANUMERIC:
            self.list.sort(key=self.buildAlphaNumericSortKey)
        else:
            if self.sort_type == MovieList.SORT_DATE_ASC:
                self.list.sort(self.sortbyDateAsc)
            else:
                self.list.sort(self.sortbyDateDesc)
#            # sort: key is 'begin'
#            self.list.sort(key=lambda x: -x[2])

        if self.show_folders:
            dirs.sort(self.sortFolders)
            for servicedirs in dirs:
                self.list.insert(0, servicedirs)
            tmp = self.root.getPath()
            if len(tmp) > 1:
                tt = eServiceReference(eServiceReference.idFile, eServiceReference.flagDirectory, "..")
                tt.setName("..")
                tmpRoot = os.path.dirname(tmp[:-1])
                if len(tmpRoot) > 1:
                    tmpRoot = tmpRoot + "/"
                tt.setPath(tmpRoot)
                self.list.insert(0, (tt, None, -1, -1))
        self.tags = tags

    def sortbyDateAsc(self, a, b):
        return cmp(a[2], b[2])

    def sortbyDateDesc(self, a, b):
        return cmp(b[2], a[2])

    def sortFolders(self, a, b):
        return cmp(b[0].getName().lower(), a[0].getName().lower())

    def buildAlphaNumericSortKey(self, x):
        ref = x[0]
        info = self.serviceHandler.info(ref)
        name = info and info.getName(ref)
        return (name and name.lower() or "", -x[2])

    def moveTo(self, serviceref):
        count = 0
        for x in self.list:
            if x[0] == serviceref:
                self.instance.moveSelectionTo(count)
                return True
            count += 1
        return False
    
    def moveDown(self):
        self.instance.moveSelection(self.instance.moveDown)

    def setMovieStatus(self, serviceref, status):
        info = self.serviceHandler.info(serviceref)
        if info is None:
            return
        cur_idx = self.l.getCurrentSelectionIndex()
        cue = info.cueSheet()
        if cue is not None:
            cutList = cue.getCutList()
            for l in cutList:
                if l[1] == 3:
                    cutList.remove(l)
            if status:
                    x = self.list[cur_idx]
                    length = x[1].getLength(x[0])
                    new = (long(length * 90000), 3)
                    cutList.append(new)
            cue.setCutList(cutList)
            self.l.invalidateEntry(cur_idx)
