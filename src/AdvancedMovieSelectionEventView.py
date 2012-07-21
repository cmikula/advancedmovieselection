#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  The plugin is developed on the basis from a lot of single plugins (thx for the code @ all)
#  Coded by JackDaniel & cmikula (c)2011
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
from Components.config import config
from ServiceProvider import ServiceEvent
from Components.ScrollLabel import ScrollLabel
from MoviePreview import MoviePreview
from Globals import SkinTools, pluginPresent
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap

class EventViewBase:    
    def __init__(self, event, ref, callback=None, similarEPGCB=None):
        self.similarEPGCB = similarEPGCB
        self.cbFunc = callback
        self.currentService = ref
        self.event = event
        self["key_red"] = StaticText("")
        self["red_button"] = Pixmap()
        self["key_green"] = StaticText("")
        self["green_button"] = Pixmap()
        self["key_yellow"] = StaticText("")
        self["yellow_button"] = Pixmap()
        self["key_blue"] = StaticText("")
        self["blue_button"] = Pixmap()        
        self["Location"] = Label()
        self["epg_description"] = ScrollLabel()
        self["Service"] = ServiceEvent()
        self["actions"] = ActionMap(["OkCancelActions", "EventViewActions", "ColorActions"],
            {
                "cancel": self.close,
                "ok": self.close,
                "red": self.red_button,
                "green": self.green_button,
                "yellow": self.yellow_button,
                "blue": self.blue_button,
                "prevEvent": self.prevEvent,
                "nextEvent": self.nextEvent,
                "pageUp": self.pageUp,
                "pageDown": self.pageDown
            })
        self.onShown.append(self.onCreate)

    def onCreate(self):
        self.setEvent(self.event)

    def prevEvent(self):
        if self.cbFunc is not None:
            self.cbFunc(self.setEvent, self.setService, -1)

    def nextEvent(self):
        if self.cbFunc is not None:
            self.cbFunc(self.setEvent, self.setService, +1)

    def setService(self, service):
        self.currentService = service
        return
        if self.isRecording:
            self["channel"].setText(_("Recording"))
        else:
            name = self.currentService.getServiceName()
            if name is not None:
                self["channel"].setText(name)
            else:
                self["channel"].setText(_("Unknown service"))

    def setEvent(self, event):
        if pluginPresent.TheTVDB:
            self["red_button"].show()
            self["key_red"].setText(_("TheTVDB search"))
        else:
            self["red_button"].hide()
            self["key_red"].setText("")
        if pluginPresent.TMDb:
            self["green_button"].show()
            self["key_green"].setText(_("TMDb search"))
        else:
            self["green_button"].hide()
            self["key_green"].setText("")
        if pluginPresent.IMDb:
            self["yellow_button"].show()
            self["key_yellow"].setText(_("IMDB search"))
        else:
            self["yellow_button"].hide()
            self["key_yellow"].setText("")
        if pluginPresent.OFDb:
            self["blue_button"].show()
            self["key_blue"].setText(_("OFDb search"))
        else:
            self["blue_button"].hide()
            self["key_blue"].setText("")
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
        self.loadPreview(serviceref)

    def pageUp(self):
        self["epg_description"].pageUp()

    def pageDown(self):
        self["epg_description"].pageDown()

    def red_button(self):
        if pluginPresent.TheTVDB:
            from Plugins.Extensions.TheTVDB.TheTVDB import TheTVDBMain
            from enigma import eServiceCenter
            ref = self.currentService
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
            eventName = title
            self.session.openWithCallback(self.close, TheTVDBMain, eventName) 
        
    def green_button(self):
        if pluginPresent.TMDb:
            from Plugins.Extensions.TMDb.plugin import TMDbMain
            from enigma import eServiceCenter
            ref = self.currentService
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
            eventName = title
            self.session.openWithCallback(self.close, TMDbMain, eventName) 
        
    def yellow_button(self):
        if pluginPresent.IMDb:
            from Plugins.Extensions.IMDb.plugin import IMDB
            from enigma import eServiceCenter
            ref = self.currentService
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
            eventName = title
            self.session.openWithCallback(self.close, IMDB, eventName)
        
    def blue_button(self):
        if pluginPresent.OFDb:
            from Plugins.Extensions.OFDb.plugin import OFDB
            from enigma import eServiceCenter
            ref = self.currentService
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
            eventName = title
            self.session.openWithCallback(self.close, OFDB, eventName)

class EventViewSimple(Screen, EventViewBase, MoviePreview):
    def __init__(self, session, event, ref, callback=None, similarEPGCB=None):
        Screen.__init__(self, session)
        self.skinName = SkinTools.appendResolution("AdvancedMovieSelectionEventView")
        EventViewBase.__init__(self, event, ref, callback, similarEPGCB)
        MoviePreview.__init__(self, session)
