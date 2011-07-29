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
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from enigma import getDesktop, ePicLoad
from Components.config import config
from Components.AVSwitch import AVSwitch
from Tools.Directories import fileExists
from ServiceProvider import ServiceEvent
import os
from Components.ScrollLabel import ScrollLabel
from Components.MenuList import MenuList

nocover = ("/usr/lib/enigma2/python/Plugins/Extensions/AdvancedMovieSelection/images/nocover_info.jpg")

class EventViewBase:    
    def __init__(self, Event, Ref, callback=None, similarEPGCB=None):
        self.similarEPGCB = similarEPGCB
        self.cbFunc = callback
        self.currentService = Ref
        self.event = Event
        self["Location"] = Label()
        self["epg_description"] = ScrollLabel()
        self["Service"] = ServiceEvent()
        self["actions"] = ActionMap(["OkCancelActions", "EventViewActions"],
            {
                "cancel": self.close,
                "ok": self.close,
                "pageUp": self.pageUp,
                "pageDown": self.pageDown
            })
        self.onShown.append(self.onCreate)

    def onCreate(self):
        self.setEvent(self.event)

    def setEvent(self, event):
        self.event = event
        if event is None:
            return
        ref = self.currentService
        description = event.getExtendedDescription()
        self["epg_description"].setText(description)
        from enigma import eServiceCenter
        serviceHandler = eServiceCenter.getInstance()
        info = serviceHandler.info(ref)
        name = info and info.getName(ref) or _("this recording")
        if name.endswith(".ts"):
            title = name[:-3]
        elif name.endswith(".mp4") or name.endswith(".mov") or name.endswith(".mkv") or name.endswith(".iso") or name.endswith(".flv") or name.endswith(".avi") or name.endswith(".ogg"):
            title = name[:-4]
        elif name.endswith(".divx") or name.endswith(".m2ts") or name.endswith(".mpeg"):
            title = name[:-5]
        else:
            title = info and info.getName(ref) or _("this recording")
        self.setTitle(_("Infos for: %s") % title)
        self["Location"].setText(_("Movie location: %s") % (config.movielist.last_videodir.value))
        serviceref = self.currentService
        self["Service"].newService(serviceref)

    def pageUp(self):
        self["epg_description"].pageUp()

    def pageDown(self):
        self["epg_description"].pageDown()

class MovielistInfoPreview(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            self.skinName = ["AdvancedMovieSelectionInfoCoverHD"]
        elif sz_w == 1024:
            self.skinName = ["AdvancedMovieSelectionInfoCoverXD"]
        else:
            self.skinName = ["AdvancedMovieSelectionInfoCoverSD"]
        self["Infobackground"] = Label("")
        self["Infopreview"] = Pixmap()

class MovieInfoPreview():
    def __init__(self, session):
        self.dialog = session.instantiateDialog(MovielistInfoPreview)
        self.onHide.append(self.hideDialog)
        self.working = False
        self.picParam = None

class EventViewSimple(Screen, EventViewBase, MovieInfoPreview):
    def __init__(self, session, Event, Ref, callback=None, similarEPGCB=None):
        Screen.__init__(self, session)
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            self.skinName = ["AdvancedMovieSelectionEventViewHD"]
        elif sz_w == 1024:
            self.skinName = ["AdvancedMovieSelectionEventViewXD"]
        else:
            self.skinName = ["AdvancedMovieSelectionEventViewSD"]
        EventViewBase.__init__(self, Event, Ref, callback, similarEPGCB)
        MovieInfoPreview.__init__(self, session)
        serviceref = self.currentService
        self.loadInfoPreview(serviceref)

    def loadInfoPreview(self, serviceref):
        self.hideDialog()
        if serviceref:
            path = serviceref.getPath()
            if not os.path.isdir(path):
                path = os.path.splitext(path)[0] + ".jpg"
            else:
                path = path + ".jpg"
            
            if fileExists(path):
                self.showDialog()
                self.working = True
                sc = AVSwitch().getFramebufferScale()
                self.picload = ePicLoad()
                self.picload.PictureData.get().append(self.showPreviewCallback)
                self.picload.setPara((self.dialog["Infopreview"].instance.size().width(), self.dialog["Infopreview"].instance.size().height(), sc[0], sc[1], False, 1, "#00000000"))
                self.dialog.hide()
                self.picload.startDecode(path)
            else:
                self.showDialog()
                self.working = True
                sc = AVSwitch().getFramebufferScale()
                self.picload = ePicLoad()
                self.picload.PictureData.get().append(self.showPreviewCallback)
                self.picload.setPara((self.dialog["Infopreview"].instance.size().width(), self.dialog["Infopreview"].instance.size().height(), sc[0], sc[1], False, 1, "#00000000"))
                self.dialog.hide()
                self.picload.startDecode(nocover)
            
    def showPreviewCallback(self, picInfo=None):
        if picInfo and self.working:
            ptr = self.picload.getData()
            if ptr != None:
                self.dialog["Infopreview"].instance.setPixmap(ptr)
                self.dialog.show()
        self.working = False

    def hideDialog(self):
        self.working = False
        self.dialog.hide()

    def showDialog(self):
        self.dialog.show()
