#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  The plugin is developed on the basis from a lot of single plugins (thx for the code @ all)
#  Coded by cmikula (c)2014
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
from Screens.ChannelSelection import ChannelContextMenu, MODE_TV
from Components.ChoiceList import ChoiceEntryComponent
from Tools.BoundFunction import boundFunction
from enigma import eServiceCenter, eServiceReference

ChannelContextMenu__init__ = None
def AMSChannelContextMenuInit():
    print "[AdvancedMovieSelection] override ChannelContextMenu.__init__"
    global ChannelContextMenu__init__
    if ChannelContextMenu__init__ is None:
        ChannelContextMenu__init__ = ChannelContextMenu.__init__
    ChannelContextMenu.__init__ = AMSChannelContextMenu__init__
    ChannelContextMenu.AMSstartTMDb = startTMDb
    ChannelContextMenu.AMSstartTVDb = startTVDb
    ChannelContextMenu.AMScloseafterfinish = closeafterfinish

def AMSChannelContextMenu__init__(self, session, csel):
    ChannelContextMenu__init__(self, session, csel)
    current = csel.getCurrentSelection()
    current_sel_path = current.getPath()
    current_sel_flags = current.flags
    if csel.mode == MODE_TV and not (current_sel_path or current_sel_flags & (eServiceReference.isDirectory|eServiceReference.isMarker)):
        self["menu"].list.insert(0, ChoiceEntryComponent(text=(_("TVDb Info (AMS)"), boundFunction(self.AMSstartTVDb))))
        self["menu"].list.insert(0, ChoiceEntryComponent(text=(_("TMDb Info (AMS)"), boundFunction(self.AMSstartTMDb))))

def startTMDb(self):
    from SearchTMDb import TMDbMain
    if isinstance(self, ChannelContextMenu):
        print "[AdvancedMovieSelection] tmdb"
        service = self.csel.servicelist.getCurrent()
        info = eServiceCenter.getInstance().info(service)
        event = info.getEvent(service)
        eventName = "22 bullets"
        if event:
            eventName = event.getEventName()
            self.session.openWithCallback(self.AMScloseafterfinish, TMDbMain, eventName) 
    else:
        info = self.session.nav.getCurrentService().info()
        event = info.getEvent(0)
        if event:
            eventName = event.getEventName()
            self.session.openWithCallback(self.AMScloseafterfinish, TMDbMain, eventName)

def startTVDb(self):
    from SearchTVDb import TheTVDBMain
    if isinstance(self, ChannelContextMenu):
        print "[AdvancedMovieSelection] tvdb"
        service = self.csel.servicelist.getCurrent()
        info = eServiceCenter.getInstance().info(service)
        event = info.getEvent(service)
        eventName = "Law & Order"
        shortdescr = ""
        if event:
            eventName = event.getEventName()
            shortdescr = event.getShortDescription()
            self.session.openWithCallback(self.AMScloseafterfinish, TheTVDBMain, None, eventName, shortdescr) 

def closeafterfinish(self, retval=None):
    self.close() 

