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
        width_up_r = 350
        width_up_l = width - width_up_r
        width_dn_r = width / 2
        width_dn_l = width - width_dn_r
        pos_up_r = width - width_up_r 
        pos_dn_r = width - width_dn_r
        begin_string = self.getBeginString(serviceref)
        description = serviceref.getShortDescription()
        service_info = "%d MB - %s" % (getServiceSize(serviceref.getPath()) / (1024 * 1024), begin_string)
        res.append(MultiContentEntryText(pos=(5, 3), size=(width_up_l, 30), font=0, flags=RT_HALIGN_LEFT, text=serviceref.getName()))
        res.append(MultiContentEntryText(pos=(5, 28), size=(width_dn_l, 30), font=1, flags=RT_HALIGN_LEFT, text=os.path.dirname(serviceref.getPath())))
        res.append(MultiContentEntryText(pos=(pos_up_r, 3), size=(width_up_r, 22), font=1, flags=RT_HALIGN_RIGHT, text=description))
        res.append(MultiContentEntryText(pos=(pos_dn_r, 28), size=(width_dn_r, 22), font=1, flags=RT_HALIGN_RIGHT, text=service_info))
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
        #self.serviceHandler = ServiceCenter.getInstance()
        if config.AdvancedMovieSelection.wastelist_buildtype.value == 'listMovies':
            trash = Trashcan.listMovies(root.getPath())
        if config.AdvancedMovieSelection.wastelist_buildtype.value == 'listAllMovies':
            trash = Trashcan.listAllMovies(root.getPath())
        if config.AdvancedMovieSelection.wastelist_buildtype.value == 'listAllMoviesMedia':
            trash = Trashcan.listAllMovies("/media")
        for service in trash:
            #info = self.serviceHandler.info(service)
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
        })
        self["key_red"] = Button(_("Delete movie"))
        self["key_green"] = Button(_("Restore movie"))
        self["key_yellow"] = Button(_("Empty Trash"))
        self["key_blue"] = Button()
        self["waitingtext"] = Label(_("Please wait... Loading trash list..."))
        self["freeDiskSpace"] = self.diskinfo = DiskInfo(config.movielist.last_videodir.value, DiskInfo.FREE, update=False)
        self["location"] = Label()
        self["warning"] = Label()
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
        if not config.AdvancedMovieSelection.askdelete.value:
            self["warning"].setText(_("ATTENTION: Ask before delete ist disabled!"))
        if not self.inited:
            self.delayTimer.start(0, 1)
            self.inited = True

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
            self.session.openWithCallback(self.delete, MessageBox, _("Do you really want to delete %s?") % (self.service.getName()))
        else:
            self.delete(True)

    def canDeleteAll(self):
        self.service = self.getCurrent()
        if not self.service:
            return
        if config.AdvancedMovieSelection.askdelete.value:
            self.session.openWithCallback(self.deleteAll, MessageBox, _("Do you really want to delete all movies?"))
        else:
            self.deleteAll(True)

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

    def deleteAll(self, confirmed):
        if not confirmed:
            return
        self["list"].hide()
        self["waitingtext"].setText(_("Deleting in progress! Please wait..."))
        self["waitingtext"].show()
        self.deleteTimer.start(0, 1)

    def deleteAllMovies(self):
        deleted = []
        try:
            for x in self.list.list:
                service = x[0]
                Trashcan.delete(service.getPath())
                deleted.append(service)
        except Exception, e:
            print e
            self.session.open(MessageBox, _("Delete failed!"), MessageBox.TYPE_ERROR)
        for service in deleted:
            self["list"].removeService(service)
        self["waitingtext"].hide()
        self["list"].show()
        
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
