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
from Screens.Screen import Screen
from Trashcan import Trashcan, eServiceReferenceTrash
from Components.config import config
from Components.ActionMap import HelpableActionMap
from Components.Button import Button
from Components.Label import Label
from ServiceProvider import detectDVDStructure
from Screens.MessageBox import MessageBox
from enigma import getDesktop, eTimer
from Tools.Directories import fileExists
from Components.DiskInfo import DiskInfo
from Components.UsageConfig import defaultMoviePath
from Components.GUIComponent import GUIComponent
from enigma import eListboxPythonMultiContent, eListbox, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT
from Components.MultiContent import MultiContentEntryText
from datetime import datetime
from Tools.Directories import getSize as getServiceSize
import os
from time import time, strftime, localtime
from MessageServer import getIpAddress
from Client import getClients
from ClientSetup import ClientSetup
from Components.Pixmap import Pixmap

staticIP = None

class TrashMovieList(GUIComponent):
    def __init__(self, root):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        
        if root is not None:
            self.reload(root)
        
        self.l.setFont(0, gFont("Regular", 22))
        self.l.setFont(1, gFont("Regular", 18))
        self.l.setItemHeight(50)
        self.l.setBuildFunc(self.buildMovieListEntry)
        
        self.onSelectionChanged = [ ]

    def connectSelChanged(self, fnc):
        if not fnc in self.onSelectionChanged:
            self.onSelectionChanged.append(fnc)

    def disconnectSelChanged(self, fnc):
        if fnc in self.onSelectionChanged:
            self.onSelectionChanged.remove(fnc)

    def selectionChanged(self):
        for x in self.onSelectionChanged:
            x()

    def buildMovieListEntry(self, serviceref, info, begin, length):
        res = [ None ]
        width = self.l.getItemSize().width()
        width_up_r = 250
        width_up_l = width - width_up_r
        width_dn_r = width / 2
        width_dn_l = width - width_dn_r
        pos_up_r = width - width_up_r 
        pos_dn_r = width - width_dn_r
        begin_string = self.getBeginString(serviceref)
        description = serviceref.getShortDescription()
        filesize = float(getServiceSize(serviceref.getPath()) / (1024 * 1024))
        if filesize <= 999:
            service_info = "%d MB - %s" % (filesize, begin_string)
        else:
            if config.AdvancedMovieSelection.filesize_digits.value == "0":
                service_info = "%d GB - %s" % ((filesize / 1000), begin_string)
            elif config.AdvancedMovieSelection.filesize_digits.value == "1":
                service_info = "%s GB - %s" % ((round(filesize / 1000, 1)), begin_string)
            elif config.AdvancedMovieSelection.filesize_digits.value == "2":
                service_info = "%s GB - %s" % ((round(filesize / 1000, 2)), begin_string)
            else:
                service_info = "%s GB - %s" % ((round(filesize / 1000, 3)), begin_string)
        res.append(MultiContentEntryText(pos=(5, 3), size=(width_up_l, 30), font=0, flags=RT_HALIGN_LEFT, text=serviceref.getName()))
        res.append(MultiContentEntryText(pos=(5, 28), size=(width_dn_l, 30), font=1, flags=RT_HALIGN_LEFT, text=os.path.dirname(serviceref.getPath())))
        res.append(MultiContentEntryText(pos=(pos_up_r - 5, 3), size=(width_up_r, 22), font=1, flags=RT_HALIGN_RIGHT, text=description))
        res.append(MultiContentEntryText(pos=(pos_dn_r - 5, 28), size=(width_dn_r, 22), font=1, flags=RT_HALIGN_RIGHT, text=service_info))
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

    def load(self, root):
        self.list = [ ]
        if not root:
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
    
    def moveDown(self):
        self.instance.moveSelection(self.instance.moveDown)

    def getBeginString(self, serviceref):
        dvd_path = detectDVDStructure(serviceref.getPath() + "/")
        if dvd_path:
            begin = long(os.stat(dvd_path).st_mtime)
        else:
            begin = long(os.stat(serviceref.getPath()).st_mtime)
        d = datetime.fromtimestamp(begin)
        return d.strftime("%d.%m.%Y %H:%M")


class Wastebasket(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            self.skinName = ["AdvancedMovieSelectionTrashHD"]
        elif sz_w == 1024:
            self.skinName = ["AdvancedMovieSelectionTrashXD"]
        else:
            self.skinName = ["AdvancedMovieSelectionTrashSD"]
        self.delayTimer = eTimer()
        self.delayTimer.callback.append(self.updateHDDData)
        self.deleteTimer = eTimer()
        self.deleteTimer.callback.append(self.deleteAllMovies)
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
        self.staticIP = getIpAddress('eth0')
        self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
            {
                "cancel": (self.abort, _("Exit wastebasket"))
            })
        self["MenuActions"] = HelpableActionMap(self, "MenuActions",
            {
                "menu": (self.clientsetup, _("Clientbox setup"))
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
            if self.staticIP:
                for client in getClients():
                    if client is not None:
                        lastEmptyEvent = client.lastTrashEvent()
                        if lastEmptyEvent != -1:
                            t = localtime(lastEmptyEvent)
                            self["autoemptylast"].setText( _("Last remote wastebasket empty at %s") % (strftime(("%02d.%02d.%04d" % (t[2], t[1], t[0])) + ' ' + _("at") + ' ' + ("%02d:%02d" % (t[3], t[4])) + ' ' + _("Clock"))))
                        nextEmptyEvent = client.nextTrashEvent()
                        if nextEmptyEvent != -1:
                            t = localtime(nextEmptyEvent)
                            self["autoemptynext"].setText(_("Next remote wastebasket empty at %s") % (strftime(("%02d.%02d.%04d" % (t[2], t[1], t[0])) + ' ' + _("at") + ' ' + ("%02d:%02d" % (t[3], t[4])) + ' ' + _("Clock"))))
                    else:
                        self["autoemptylast"].setText(_("No last empty status available!"))
                        self["autoemptynext"].setText(_("No next empty status available!"))
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
        self.getWasteInfo()

    def getWasteInfo(self):
        count = Trashcan.getTrashCount()
        cap = Trashcan.getTrashSize()
        if cap <= 999:
            wastebasket_info = (_("Trash count: %s") % count) + ' / ' + (_("Trash size: %d MB") % cap)
        else:
            if config.AdvancedMovieSelection.filesize_digits.value == "0":
                wastebasket_info = (_("Trash count: %s") % count) + ' / ' + (_("Trash size: %d GB") % cap / 1000)
            elif config.AdvancedMovieSelection.filesize_digits.value == "1":
                wastebasket_info = (_("Trash count: %s") % count) + ' / ' + (_("Trash size: %s GB") % cap / 1000, 1)
            elif config.AdvancedMovieSelection.filesize_digits.value == "2":
                wastebasket_info = (_("Trash count: %s") % count) + ' / ' + (_("Trash size: %s GB") % cap / 1000, 2)
            else:
                wastebasket_info = (_("Trash count: %s") % count) + ' / ' + (_("Trash size: %s GB") % cap / 1000, 3)
        if count == 0:
            self["wastetxt"].setText(_("Wastebasket is empty!"))
        else:
            self["wastetxt"].setText(wastebasket_info)

    def clientsetup(self):
        self.session.open(ClientSetup)

    def getCurrent(self):
        self.session.currentSelection = self["list"].getCurrent()
        return self.session.currentSelection

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
            Trashcan.delete(self.service.getPath())
        except Exception, e:
            print e
            self.session.open(MessageBox, _("Delete failed!"), MessageBox.TYPE_ERROR)
            return
        
        self["list"].removeService(self.service)

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
        self["waitingtext"].setText(_("Deleting in progress! Please wait..."))
        self["waitingtext"].show()
        self.deleteTimer.start(0, 1)

    def deleteAllMovies(self):
        try:
            print "Start deleting all movies in trash list"
            for x in self.list.list[:]:
                service = x[0]
                Trashcan.delete(service.getPath())
                self["list"].removeService(service)
        except Exception, e:
            print e
            self.session.open(MessageBox, _("Delete failed!"), MessageBox.TYPE_ERROR)
        self.close()
        
    def restore(self):
        try:
            if not self.getCurrent():
                return
            Trashcan.restore(self.getCurrent().getPath())
        except Exception, e:
            print e
            self.session.open(MessageBox, _("Restore failed!"), MessageBox.TYPE_ERROR)
            return
        
        self["list"].removeService(self.getCurrent())

    def restoreAll(self):
        try:
            print "Start restoring all movies"
            for x in self.list.list[:]:
                service = x[0]
                Trashcan.restore(service.getPath())
                self["list"].removeService(service)
        except Exception, e:
            print e
            self.session.open(MessageBox, _("Restore failed!"), MessageBox.TYPE_ERROR)
        self.close()
