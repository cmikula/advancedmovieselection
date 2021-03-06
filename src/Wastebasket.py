#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Copyright (C) 2011 cmikula

Trash can gui for Advanced Movie Selection

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

from __init__ import _
import os
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Source.Trashcan import Trashcan, eServiceReferenceTrash
from Components.config import config
from Components.ActionMap import HelpableActionMap
from Components.Button import Button
from Components.Label import Label
from Source.ServiceProvider import detectDVDStructure
from Screens.MessageBox import MessageBox
from Source.Timer import xTimer
from Tools.Directories import fileExists
from Components.DiskInfo import DiskInfo
from Components.UsageConfig import defaultMoviePath
from GUIListComponent import GUIListComponent
from enigma import RT_HALIGN_LEFT, RT_HALIGN_RIGHT
from Components.MultiContent import MultiContentEntryText
from datetime import datetime
from Tools.Directories import getSize as getServiceSize
from time import time, strftime, localtime
from Components.Pixmap import Pixmap
from Source.ServiceUtils import realSize
from SkinParam import WastebasketSkinParam

class TrashMovieList(WastebasketSkinParam, GUIListComponent):
    def __init__(self, root):
        GUIListComponent.__init__(self)
        WastebasketSkinParam.__init__(self)
        self.l.setBuildFunc(self.buildMovieListEntry)
        self.onSelectionChanged = [ ]
        if root is not None:
            self.reload(root)

    def buildMovieListEntry(self, serviceref, info, begin, length):
        res = [ None ]
        width = self.l.getItemSize().width()
        date = _("Record date:") + ' ' + self.getDate(serviceref)
        time = _("Record time:") + ' ' + self.getTime(serviceref)
        description = serviceref.getShortDescription()
        filesize = realSize(getServiceSize(serviceref.getPath()), int(config.AdvancedMovieSelection.filesize_digits.value))
        res.append(MultiContentEntryText(pos=(self.line1Pos.x(), self.line1Pos.y()), size=(width - self.line1Pos.x() - self.line1Split, self.f0h), font=0, flags=RT_HALIGN_LEFT, text=serviceref.getName()))
        res.append(MultiContentEntryText(pos=(self.line2Pos.x(), self.line2Pos.y()), size=(width - self.line2Pos.x() - self.line2Split, self.f1h), font=1, flags=RT_HALIGN_LEFT, text=description))
        res.append(MultiContentEntryText(pos=(self.line3Pos.x(), self.line3Pos.y()), size=(width - self.line3Pos.x() - self.line3Split, self.f2h), font=2, flags=RT_HALIGN_LEFT, text=os.path.dirname(serviceref.getPath())))
        res.append(MultiContentEntryText(pos=(width - self.line1Split, self.line1Pos.y()), size=(self.line1Split - self.line1Pos.x(), self.f0h), font=0, flags=RT_HALIGN_RIGHT, text=filesize))
        res.append(MultiContentEntryText(pos=(width - self.line2Split, self.line2Pos.y()), size=(self.line2Split - self.line2Pos.x(), self.f1h), font=1, flags=RT_HALIGN_RIGHT, text=time))
        res.append(MultiContentEntryText(pos=(width - self.line3Split, self.line3Pos.y()), size=(self.line3Split - self.line3Pos.x(), self.f2h), font=2, flags=RT_HALIGN_RIGHT, text=date))
        return res

    def getCurrentEvent(self):
        l = self.l.getCurrentSelection()
        return l and l[0] and l[1] and l[1].getEvent(l[0])

    def load(self, root):
        self.list = [ ]
        if not root or Trashcan.isCurrentlyDeleting():
            return
        if config.AdvancedMovieSelection.wastelist_buildtype.value == 'listMovies':
            trash = Trashcan.listMovies(root.getPath())
        if config.AdvancedMovieSelection.wastelist_buildtype.value == 'listAllMovies':
            trash = Trashcan.listAllMovies(root.getPath())
        if config.AdvancedMovieSelection.wastelist_buildtype.value == 'listAllMoviesMedia':
            trash = Trashcan.listAllMovies("/media")
        for service in trash:
            self.list.append((service, None, -1, -1))

    def reload(self, root=None):
        self.load(root)
        self.l.setList(self.list)

    def removeService(self, service):
        for l in self.list[:]:
            if l[0] == service:
                self.list.remove(l)
        self.l.setList(self.list)

    def __len__(self):
        return len(self.list)

    def moveTo(self, serviceref):
        count = 0
        for x in self.list:
            if x[0] == serviceref:
                self.instance.moveSelectionTo(count)
                return True
            count += 1
        return False
    
    def getDate(self, serviceref):
        dvd_path = detectDVDStructure(serviceref.getPath() + "/")
        if dvd_path:
            begin = long(os.stat(dvd_path).st_mtime)
        else:
            begin = long(os.stat(serviceref.getPath()).st_mtime)
        d = datetime.fromtimestamp(begin)
        return d.strftime("%d.%m.%Y")

    def getTime(self, serviceref):
        dvd_path = detectDVDStructure(serviceref.getPath() + "/")
        if dvd_path:
            begin = long(os.stat(dvd_path).st_mtime)
        else:
            begin = long(os.stat(serviceref.getPath()).st_mtime)
        d = datetime.fromtimestamp(begin)
        return d.strftime("%H:%M")
    
class Wastebasket(Screen, HelpableScreen):
    def __init__(self, session):
        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        self.skinName = "AdvancedMovieSelectionTrash"
        self.delayTimer = xTimer()
        self.delayTimer.addCallback(self.updateHDDData)
        self.current_ref = eServiceReferenceTrash(config.movielist.last_videodir.value)  
        self["ColorActions"] = HelpableActionMap(self, "ColorActions",
        {
            "red": (self.canDelete, _("Delete selected movie")),
            "green": (self.restore, _("Restore movie")),
            "yellow": (self.canDeleteAll, _("Empty wastbasket")),
            "blue": (self.restoreAll, _("Restore all movies")),
        })
        self["key_red"] = Button(_("Delete movie"))
        self["key_green"] = Button(_("Restore movie"))
        self["key_yellow"] = Button(_("Empty Trash"))
        self["key_blue"] = Button(_("Restore all movies"))
        self["waitingtext"] = Label(_("Please wait... Loading trash list..."))
        self["freeDiskSpace"] = self.diskinfo = DiskInfo(config.movielist.last_videodir.value, DiskInfo.FREE, update=False)
        self["location"] = Label()
        self["warning"] = Label()
        self["wastetxt"] = Label()
        self["MenuIcon"] = Pixmap()
        self["autoemptylast"] = Label()
        self["autoemptynext"] = Label()
        self["list"] = TrashMovieList(None)
        self.list = self["list"]
        self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
            {
                "cancel": (self.abort, _("Exit wastebasket"))
            })
        self.inited = False
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_("Advanced Movie Selection - Wastebasket"))
        if not config.AdvancedMovieSelection.askdelete.value and config.AdvancedMovieSelection.showinfo.value:
            self["warning"].setText(_("ATTENTION: Ask before delete is disabled!"))
        if not self.inited:
            self.delayTimer.start(0, 1)
            self.inited = True
        value = int(config.AdvancedMovieSelection.auto_empty_wastebasket.value)
        if value != -1:
            if config.AdvancedMovieSelection.last_auto_empty_wastebasket.value == 0:
                self["autoemptylast"].setText(_("Last automated wastebasket empty:") + ' ' + _("Never!"))
            else:
                t = localtime(config.AdvancedMovieSelection.last_auto_empty_wastebasket.value)
                lastUpdateCheck_time = strftime(("%02d.%02d.%04d" % (t[2], t[1], t[0])) + ' ' + _("at") + ' ' + ("%02d:%02d" % (t[3], t[4])) + ' ' + _("Clock"))
                self["autoemptylast"].setText(_("Last automated wastebasket empty at %s") % lastUpdateCheck_time)
            t = localtime(config.AdvancedMovieSelection.next_auto_empty_wastebasket.value)
            nextUpdateCheck_time = strftime(("%02d.%02d.%04d" % (t[2], t[1], t[0])) + ' ' + _("at") + ' ' + ("%02d:%02d" % (t[3], t[4])) + ' ' + _("Clock"))
            self["autoemptynext"].setText(_("Next automated wastebasket empty at %s") % nextUpdateCheck_time)
        else:
            self["autoemptylast"].setText(_("Auto empty wastebasket is disabled"))

    def updateHDDData(self):
        self.reloadList(self.current_ref)
        self["waitingtext"].hide()

    def reloadList(self, sel=None, home=False):
        if not fileExists(config.movielist.last_videodir.value):
            path = defaultMoviePath()
            config.movielist.last_videodir.value = path
            config.movielist.last_videodir.save()
            self.current_ref = eServiceReferenceTrash(path)
            self["freeDiskSpace"].path = path
        if sel is None:
            sel = self.getCurrent()
        self["list"].reload(self.current_ref)
        if config.AdvancedMovieSelection.wastelist_buildtype.value == 'listAllMoviesMedia':
            title = _("Wastebasket: %s") % ("/media")
        else:
            title = _("Wastebasket: %s") % (config.movielist.last_videodir.value)
        self["location"].setText(title)
        if not (sel and self["list"].moveTo(sel)):
            if home:
                self["list"].moveToIndex(0)
        self["freeDiskSpace"].update()
        count = Trashcan.getTrashCount()
        cap = Trashcan.getTrashSize()
        if cap <= 999:
            wastebasket_info = (_("Trash count: %d") % (count)) + ' / ' + (_("Trash size: %d MB") % cap)
        else:
            format_string = _("Trash size:") + " %%.%sf GB" % (config.AdvancedMovieSelection.filesize_digits.value)
            wastebasket_info = _("Trash count:") + (" %d / " % (count)) + (format_string) % (cap / 1000.0)
        if count == 0:
            self["wastetxt"].setText(_("Wastebasket is empty!"))
        else:
            self["wastetxt"].setText(wastebasket_info)

    def getCurrent(self):
        return self["list"].getCurrent()

    def abort(self):
        self.close()

    def canDelete(self):
        self.service = self.getCurrent()
        if not self.service:
            return
        if config.AdvancedMovieSelection.askdelete.value:
            self.session.openWithCallback(self.canDeleteCheckRecord, MessageBox, _("Do you really want to delete %s?") % (self.service.getName()))
        else:
            self.canDeleteCheckRecord(True)

    def canDeleteCheckRecord(self, confirmed):
        if not confirmed:
            return
        recordings = self.session.nav.getRecordings()
        next_rec_time = -1
        if not recordings:
            next_rec_time = self.session.nav.RecordTimer.getNextRecordingTime()	
        if config.movielist.last_videodir.value == "/hdd/movie/" and recordings or (next_rec_time > 0 and (next_rec_time - time()) < 360):
            self.session.openWithCallback(self.delete, MessageBox, _("Recording(s) are in progress or coming up in few seconds!\nNow movie delete can damage the recording(s)!\nRealy delete movie?"))
        else:
            self.delete(True)

    def canDeleteAll(self):
        self.service = self.getCurrent()
        if not self.service:
            return
        if config.AdvancedMovieSelection.askdelete.value:
            self.session.openWithCallback(self.deleteAllcheckRecord, MessageBox, _("Do you really want to delete all movies?"))
        else:
            self.deleteAllcheckRecord(True)

    def delete(self, confirmed):
        if not confirmed:
            return
        try:
            self["list"].removeService(self.service)
            Trashcan.delete(self.service.getPath())
        except Exception, e:
            print e
            self.session.open(MessageBox, _("Delete failed!"), MessageBox.TYPE_ERROR)
            return
        self.delayTimer.start(0, 1)

    def deleteAllcheckRecord(self, confirmed):
        if not confirmed:
            return
        recordings = self.session.nav.getRecordings()
        next_rec_time = -1
        if not recordings:
            next_rec_time = self.session.nav.RecordTimer.getNextRecordingTime()	
        if config.movielist.last_videodir.value == "/hdd/movie/" and recordings or (next_rec_time > 0 and (next_rec_time - time()) < 360):
            self.session.openWithCallback(self.deleteAll, MessageBox, _("Recording(s) are in progress or coming up in few seconds!\nNow empty the Wastebasket can damage the recording(s)!\nRealy empty the Wastbasket?"))
        else:
            self.deleteAll(True)

    def deleteAll(self, confirmed):
        if not confirmed:
            return
        self["list"].hide()
        trash = []
        for x in self.list.list:
            service = x[0]
            trash.append(service)
        Trashcan.deleteAsynch(trash)
        self.close()

    def restore(self):
        try:
            service = self.getCurrent() 
            if not service:
                return
            self["list"].removeService(service)
            Trashcan.restore(service.getPath())
        except Exception, e:
            print e
            self.session.open(MessageBox, _("Restore failed!"), MessageBox.TYPE_ERROR)
            return
        self.delayTimer.start(0, 1)        

    def restoreAll(self):
        try:
            print "Start restoring all movies"
            for x in self.list.list[:]:
                service = x[0]
                self["list"].removeService(service)
                Trashcan.restore(service.getPath())
        except Exception, e:
            print e
            self.session.open(MessageBox, _("Restore failed!"), MessageBox.TYPE_ERROR)
        self.close()

import Screens.Standby
from time import mktime
from datetime import timedelta
class WastebasketTimer():
    def __init__(self, session):
        self.session = session
        self.recTimer = xTimer()
        self.recTimer.addCallback(self.autoDeleteAllMovies)
        self.wastebasketTimer = xTimer()
        self.wastebasketTimer.addCallback(self.autoDeleteAllMovies)
        self.startTimer()
        config.AdvancedMovieSelection.empty_wastebasket_time.addNotifier(self.startTimer, initial_call=False)
    
    def stopTimer(self):
        print "[AdvancedMovieSelection] WastebasketTimer.stopTimer"
        self.wastebasketTimer.stop()
    
    def startTimer(self, dummy=None):
        if self.wastebasketTimer.isActive():
            self.wastebasketTimer.stop()
        value = int(config.AdvancedMovieSelection.auto_empty_wastebasket.value)
        cfgNext = config.AdvancedMovieSelection.next_auto_empty_wastebasket.value
        print "[AdvancedMovieSelection] WastebasketTimer.startTimer", str(value)
        print "[AdvancedMovieSelection] Read next autoclean timestamp: ", str(cfgNext)
        if value != -1:
            nowSec = int(time())
            nextUpdateSeconds = 0
            if cfgNext != None:
                # Saved timestamp found
                # No slack necessary here - we will not reach this code path
                # from autoDeleteAllMovies() as configChange() made sure to get
                # rid of next_auto_empty_wastebasket, so it cannot get into
                # some self-retriggering loop:
                if int(cfgNext) > nowSec:
                    nextUpdateSeconds = int(cfgNext)
                    print "[AMSDebug] Try to reuse timestamp: ", nextUpdateSeconds

            if nextUpdateSeconds == 0:
                # No usable saved timestamp, so we have to recompute
                now = localtime(nowSec)
                w_h = config.AdvancedMovieSelection.empty_wastebasket_time.value[0]
                w_m = config.AdvancedMovieSelection.empty_wastebasket_time.value[1]
                dt = datetime(now.tm_year, now.tm_mon, now.tm_mday, w_h, w_m)
                if value == 1:
                    nextUpdateSeconds = int(mktime(dt.timetuple()))
                    if nowSec > nextUpdateSeconds:
                        dt += timedelta(value)
                        nextUpdateSeconds = int(mktime(dt.timetuple()))
                else:
                    dt += timedelta(value)
                    nextUpdateSeconds = int(mktime(dt.timetuple()))

                # Save it so it survives e2 restart(s)
                config.AdvancedMovieSelection.next_auto_empty_wastebasket.value = nextUpdateSeconds
                config.AdvancedMovieSelection.next_auto_empty_wastebasket.save()

            # We now have a timestamp either way - start timer
            self.wastebasketTimer.startLongTimer(nextUpdateSeconds - nowSec)
            print "[AdvancedMovieSelection] Next wastebasket auto empty at", strftime("%c", localtime(nextUpdateSeconds))

        else:
            print "[AdvancedMovieSelection] Get rid of lingering next autoclean timestamp"
            config.AdvancedMovieSelection.next_auto_empty_wastebasket.value = 0
            config.AdvancedMovieSelection.next_auto_empty_wastebasket.save()
            if self.wastebasketTimer.isActive():
                self.wastebasketTimer.stop()
            if self.recTimer.isActive():
                self.recTimer.stop()

    def configChange(self):
        print "[AdvancedMovieSelection] Setup values have changed"
        config.AdvancedMovieSelection.next_auto_empty_wastebasket.value = 0
        self.startTimer()
        
    def autoDeleteAllMovies(self):
        retryvalue = "%s minutes" % int(config.AdvancedMovieSelection.next_empty_check.value)

        if self.recTimer.isActive():
            self.recTimer.stop()

        if not Screens.Standby.inStandby:
            print "[AdvancedMovieSelection] Start automated deleting all movies but box not in standby, retry in", retryvalue
            self.recTimer.start(config.AdvancedMovieSelection.next_empty_check.value * 60000)
        else:
            recordings = self.session.nav.getRecordings()
            next_rec_time = -1
            if not recordings:
                next_rec_time = self.session.nav.RecordTimer.getNextRecordingTime()    
            if config.movielist.last_videodir.value == "/hdd/movie/" and recordings or (next_rec_time > 0 and (next_rec_time - time()) < 360):           
                print "[AdvancedMovieSelection] Start automated deleting all movies but recordings activ, retry at", retryvalue
                self.recTimer.start(config.AdvancedMovieSelection.next_empty_check.value * 60000)
            else:
                if self.recTimer.isActive():
                    self.recTimer.stop()
                self.list = [ ]
                
                path = config.movielist.last_videodir.value
                if not fileExists(path):
                    path = defaultMoviePath()
                    config.movielist.last_videodir.value = path
                    config.movielist.last_videodir.save()
                    
                if config.AdvancedMovieSelection.wastelist_buildtype.value == 'listMovies':
                    trash = Trashcan.listMovies(path)
                elif config.AdvancedMovieSelection.wastelist_buildtype.value == 'listAllMovies':
                    trash = Trashcan.listAllMovies(path)
                else:
                    trash = Trashcan.listAllMovies("/media")
                
                print "[AdvancedMovieSelection] Start automated deleting all movies in trash list"
                min_age = config.AdvancedMovieSelection.empty_wastebasket_min_age.value * 86400
                print "[AdvancedMovieSelection] wastebasket retention min_age", min_age
                Trashcan.deleteAsynch(trash, min_age)
                config.AdvancedMovieSelection.last_auto_empty_wastebasket.value = int(time())
                config.AdvancedMovieSelection.last_auto_empty_wastebasket.save()
                self.configChange()

waste_timer = None

def createWasteTimer(session):
    global waste_timer
    waste_timer = WastebasketTimer(session)
    value = int(config.AdvancedMovieSelection.auto_empty_wastebasket.value)
    if value != -1:
        print "[AdvancedMovieSelection] Auto empty from wastebasket enabled..."
    else:
        waste_timer.stopTimer()
        print "[AdvancedMovieSelection] Auto empty from wastebasket disabled..."

def configChange():
    if waste_timer:
        waste_timer.configChange()
