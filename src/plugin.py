#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  The plugin is developed on the basis from a lot of single plugins (thx for the code @ all)
#  Coded by cmikula & JackDaniel (c)2012
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
from Plugins.Plugin import PluginDescriptor
from Screens.InfoBar import InfoBar
from Components.config import config
from AdvancedMovieSelectionSetup import AdvancedMovieSelectionSetup
from TagEditor import TagEditor
from Source.Config import initializeConfig
from Source.Globals import isDreamOS

initializeConfig()

def sessionstart(reason, **kwargs):
    if reason == 0:
        session = kwargs["session"]
        if not config.AdvancedMovieSelection.ml_disable.value:
            try:
                from MoviePlayer import showMovies
                value = config.AdvancedMovieSelection.movie_launch.value
                if value == "showMovies": InfoBar.showMovies = showMovies
                elif value == "showTv": InfoBar.showTv = showMovies
                elif value == "showRadio": InfoBar.showRadio = showMovies
                elif value == "timeshiftStart": InfoBar.startTimeshift = showMovies
                from Wastebasket import createWasteTimer
                createWasteTimer(session)
                
                from Source.EpgListExtension import epgListExtension
                epgListExtension.setEnabled(config.AdvancedMovieSelection.epg_extension.value)
                
                from Source.MovieScanner import movieScanner
                movieScanner.setEnabled(True)
            except:
                print '-' * 50
                import traceback, sys
                traceback.print_exc(file=sys.stdout)
                print '-' * 50

def pluginOpen(session, **kwargs):
    from MoviePlayer import initPlayerChoice
    initPlayerChoice(session)
    from MovieSelection import MovieSelection
    from MoviePlayer import playerChoice
    session.openWithCallback(playerChoice.playService, MovieSelection)

def openProgress(session, **kwargs):
    from MoveCopy import MoveCopyProgress
    session.open(MoveCopyProgress)

def pluginMenu(session, **kwargs):
    session.open(AdvancedMovieSelectionSetup)

def Setup(menuid, **kwargs):
    if (not isDreamOS and menuid == "setup") or menuid == "services_recordings":
        return [(_("Setup Advanced Movie Selection"), pluginMenu, "SetupAdvancedMovieSelection", None)]
    return []

def tmdbInfo(session, service=None, **kwargs):
    from MovieDBChannelContext import getInfo
    eventName, shortDescription = getInfo(session, service)
    if eventName:
        from SearchTMDb import TMDbMain
        session.open(TMDbMain, eventName)
        
def tvdbInfo(session, service=None, **kwargs):
    from MovieDBChannelContext import getInfo
    eventName, shortDescription = getInfo(session, service)
    if eventName:
        from SearchTVDb import TheTVDBMain
        session.open(TheTVDBMain, None, eventName, shortDescription) 

def Plugins(**kwargs):
    try:
        if config.AdvancedMovieSelection.debug.value:
            config.AdvancedMovieSelection.debug.value = False
            config.AdvancedMovieSelection.debug.save() 
        if not config.AdvancedMovieSelection.ml_disable.value:
            from Screens.MovieSelection import setPreferredTagEditor
            setPreferredTagEditor(TagEditor)
        if not config.AdvancedMovieSelection.ml_disable.value and config.AdvancedMovieSelection.useseekbar.value:
            from Seekbar import Seekbar
    except Exception, e:
        print e
    
    descriptors = []
    descriptors.append(PluginDescriptor(name=_("Setup Advanced Movie Selection"), where=PluginDescriptor.WHERE_PLUGINMENU, description=_("Alternate Movie Selection"), fnc=pluginMenu, needsRestart=True))
    descriptors.append(PluginDescriptor(where=PluginDescriptor.WHERE_MENU, description=_("Alternate Movie Selection"), fnc=Setup, needsRestart=True))
    if not config.AdvancedMovieSelection.ml_disable.value:
        descriptors.append(PluginDescriptor(name=_("Advanced Movie Selection"), where=PluginDescriptor.WHERE_SESSIONSTART, description=_("Alternate Movie Selection"), fnc=sessionstart, needsRestart=True))
        descriptors.append(PluginDescriptor(name=_("Advanced Movie Selection"), where=PluginDescriptor.WHERE_EXTENSIONSMENU, description=_("Alternate Movie Selection"), fnc=pluginOpen))
        descriptors.append(PluginDescriptor(name=_("Move Copy Progress"), where=PluginDescriptor.WHERE_EXTENSIONSMENU, description=_("Show progress of move or copy job"), fnc=openProgress))
    
        from MovieDBChannelContext import AMSEPGSelectionInit
        AMSEPGSelectionInit()
        descriptors.append(PluginDescriptor(name=_("TMDb Info (AMS)"), where=PluginDescriptor.WHERE_EVENTINFO, description=_("TMDb Info (AMS)"), fnc=tmdbInfo))
        descriptors.append(PluginDescriptor(name=_("TVDb Info (AMS)"), where=PluginDescriptor.WHERE_EVENTINFO, description=_("TVDb Info (AMS)"), fnc=tvdbInfo))
        try:
            # not implemented in oe1.6
            descriptors.append(PluginDescriptor(name=_("TMDb Info (AMS)"), where=PluginDescriptor.WHERE_CHANNEL_CONTEXT_MENU, description=_("TMDb Info (AMS)"), fnc=tmdbInfo))
            descriptors.append(PluginDescriptor(name=_("TVDb Info (AMS)"), where=PluginDescriptor.WHERE_CHANNEL_CONTEXT_MENU, description=_("TVDb Info (AMS)"), fnc=tvdbInfo))
        except:
            from MovieDBChannelContext import AMSChannelContextMenuInit
            AMSChannelContextMenuInit()
    return descriptors
