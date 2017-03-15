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
from Components.ActionMap import ActionMap
from Components.config import config
from Screens.EpgSelection import EPGSelection, EPG_TYPE_SINGLE
from Screens.ChannelSelection import ChannelContextMenu, MODE_TV
from Screens.Screen import Screen
from Components.ChoiceList import ChoiceList, ChoiceEntryComponent
from Tools.BoundFunction import boundFunction
from enigma import eServiceCenter, eServiceReference

def getInfo(session, service):
    eventName = ""
    shortdescr = ""
    if isinstance(service, str):
        eventName = service
        print "[AdvancedMovieSelection] name:", eventName
    elif isinstance(service, eServiceReference):
        info = eServiceCenter.getInstance().info(service)
        event = info.getEvent(service)
        if event:
            eventName = event.getEventName()
            shortdescr = event.getShortDescription()
        print "[AdvancedMovieSelection] service name:", eventName
    else:
        s = session.nav.getCurrentService()
        info = s.info()
        event = info.getEvent(0)
        if event:
            eventName = event.getEventName()
            shortdescr = event.getShortDescription()
        print "[AdvancedMovieSelection] current name:", eventName
    return eventName, shortdescr

ChannelContextMenu__init__ = None
def AMSChannelContextMenuInit():
    print "[AdvancedMovieSelection] override ChannelContextMenu.__init__"
    global ChannelContextMenu__init__
    if ChannelContextMenu__init__ is None:
        ChannelContextMenu__init__ = ChannelContextMenu.__init__
    ChannelContextMenu.__init__ = AMSChannelContextMenu__init__
    ChannelContextMenu.AMSstartTMDb = startTMDb
    ChannelContextMenu.AMSstartTVDb = startTVDb
    ChannelContextMenu.AMSstartTMDbSeries = startTMDbSeries
    ChannelContextMenu.AMScloseafterfinish = closeafterfinish

def AMSChannelContextMenu__init__(self, session, csel):
    ChannelContextMenu__init__(self, session, csel)
    current = csel.getCurrentSelection()
    current_sel_path = current.getPath()
    current_sel_flags = current.flags
    if csel.mode == MODE_TV and not (current_sel_path or current_sel_flags & (eServiceReference.isDirectory|eServiceReference.isMarker)):
        self["menu"].list.insert(0, ChoiceEntryComponent(text=(_("TVDb Info (AMS)"), boundFunction(self.AMSstartTVDb))))
        self["menu"].list.insert(0, ChoiceEntryComponent(text=(_("TMDb Series (AMS)"), boundFunction(self.AMSstartTMDbSeries))))
        self["menu"].list.insert(0, ChoiceEntryComponent(text=(_("TMDb Info (AMS)"), boundFunction(self.AMSstartTMDb))))

def startTMDb(self):
    from SearchTMDb import TMDbMain
    print "[AdvancedMovieSelection] tmdb"
    service = self.csel.servicelist.getCurrent()
    eventName, shortDescription = getInfo(self.session, service)
    if eventName:
        self.session.openWithCallback(self.AMScloseafterfinish, TMDbMain, eventName) 

def startTVDb(self):
    from SearchTVDb import TheTVDBMain
    print "[AdvancedMovieSelection] tvdb"
    service = self.csel.servicelist.getCurrent()
    eventName, shortDescription = getInfo(self.session, service)
    if eventName:
        self.session.openWithCallback(self.AMScloseafterfinish, TheTVDBMain, None, eventName, shortDescription) 

def startTMDbSeries(self):
    from SearchTMDbSeries import TMDbSeriesMain
    print "[AdvancedMovieSelection] tmdb series"
    service = self.csel.servicelist.getCurrent()
    eventName, shortDescription = getInfo(self.session, service)
    if service:
        self.session.openWithCallback(self.AMScloseafterfinish, TMDbSeriesMain, None, eventName, shortDescription) 


def closeafterfinish(self, retval=None):
    self.close() 


EPGSelection_enterDateTime = None
def AMSEPGSelectionInit():
    print "[AdvancedMovieSelection] override EPGSelection.enterDateTime"
    global EPGSelection_enterDateTime
    if EPGSelection_enterDateTime is None:
        EPGSelection_enterDateTime = EPGSelection.enterDateTime
        EPGSelection.enterDateTime = AMSenterDateTime
        EPGSelection.openOutdatedEPGSelection = openOutdatedEPGSelection
    
def AMSenterDateTime(self):
    event = self["Event"].event
    if self.type == EPG_TYPE_SINGLE and event:
        self.session.openWithCallback(self.openOutdatedEPGSelection, MovieDBContextMenu, event, self)
        return
    EPGSelection_enterDateTime(self)

def openOutdatedEPGSelection(self, reason=None):
    if reason == 1:
        EPGSelection_enterDateTime(self)

class MovieDBContextMenu(Screen):
    def __init__(self, session, event, epg):
        Screen.__init__(self, session)
        self.skinName = "ChannelContextMenu"
        #raise Exception("we need a better summary screen here")
        self.event = event
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "NumberActions"],
            {
                "ok": self.okbuttonClick,
                "cancel": self.cancelClick,
            })
        menu = [ ]

        menu.append(ChoiceEntryComponent(text = (_("TMDb Info (AMS)"), self.openTMDb)))
        menu.append(ChoiceEntryComponent(text = (_("TMDb Series (AMS)"), self.openTMDbSeries)))
        menu.append(ChoiceEntryComponent(text = (_("TVDb Info (AMS)"), self.openTVDb)))
        try:
            from Screens.EpgSelection import OutdatedEPGSelection
            if config.misc.epgcache_outdated_timespan.value and not isinstance(epg, OutdatedEPGSelection):
                menu.append(ChoiceEntryComponent(text = (_("Outdated EPG"), self.closeOutdated)))
        except:
            pass
        self["menu"] = ChoiceList(menu)

    def okbuttonClick(self):
        self["menu"].getCurrent()[0][1]()

    def cancelClick(self):
        self.close(False)

    def openTMDb(self):
        from SearchTMDb import TMDbMain
        eventName = self.event.getEventName()
        self.session.openWithCallback(self.closeafterfinish, TMDbMain, eventName) 
        
    def openTVDb(self):
        from SearchTVDb import TheTVDBMain
        eventName = self.event.getEventName()
        shortDescription = self.event.getShortDescription()
        self.session.openWithCallback(self.closeafterfinish, TheTVDBMain, None, eventName, shortDescription) 

    def openTMDbSeries(self):
        from SearchTMDbSeries import TMDbSeriesMain
        eventName = self.event.getEventName()
        shortDescription = self.event.getShortDescription()
        self.session.openWithCallback(self.closeafterfinish, TMDbSeriesMain, None, eventName, shortDescription) 
        
    def closeafterfinish(self, retval=None):
        self.close()
    
    def closeOutdated(self, retval=None):
        self.close(1)
