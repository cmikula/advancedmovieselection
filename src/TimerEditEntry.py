#!/usr/bin/python
# -*- coding: utf-8 -*-
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  Coded by cmikula  (c)2018
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
from Components.Sources.StaticText import StaticText
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Screens.Screen import Screen
from Components.config import config, ConfigSelection, getConfigListEntry

def getTimerEditEntry():
    return TimerEditEntry()

config.AdvancedMovieSelection.timer_download_type = ConfigSelection(default="tmdb_movie" ,
                                                                    choices=[("" , _("no")),
                                                                          ("tmdb_movie" , _("TMDb movie")),
                                                                          ("tmdb_serie" , _("TMDb serie")),
                                                                          ("tvdb_serie" , _("TVDb serie")),
                                                                          ])

class TimerEditEntry(dict):
    def __init__(self):
        self["setupFnc"] = TimerEditEntrySetup
        self["configListEntry"] = TimerEditEntrySetup.getConfigListEntry
    
class TimerEditEntrySetup(ConfigListScreen, Screen):
    def __init__(self, session, configentry, private_data, timer):
        Screen.__init__(self, session)
        self["setupActions"] = ActionMap(["ColorActions", "OkCancelActions"],
        {
            "ok": self.keyExit,
            "cancel": self.keyCancel,
            "red": self.keyCancel,
            "green": self.keySave,
        }, -2)
        self["key_red"] = StaticText(_("Close"))
        self["key_green"] = StaticText(_("Save"))
        self.list = []
        self.list.append(self.getConfigListEntry())
        ConfigListScreen.__init__(self, self.list, session)
        self.onLayoutFinish.append(self.layoutFinished)

    @staticmethod
    def getConfigListEntry():
        return getConfigListEntry(_("Cover download"), config.AdvancedMovieSelection.timer_download_type)

    def layoutFinished(self):
        self.setTitle(_("AMS cover download after timer ended"))

    def keySave(self):
        config.AdvancedMovieSelection.timer_download_type.save()
        self.keyExit()

    def keyCancel(self):
        config.AdvancedMovieSelection.timer_download_type.cancel()
        self.keyExit()

    def keyExit(self):
        self.close(config.AdvancedMovieSelection.timer_download_type.value)



