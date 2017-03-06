#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Copyright (C) 2017 cmikula

SelectionListScreen for Advanced Movie Selection

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
from Components.ActionMap import HelpableActionMap
from Components.Sources.StaticText import StaticText
from Screens.HelpMenu import HelpableScreen
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, ConfigYesNo

class SelectionListScreen(ConfigListScreen, Screen, HelpableScreen):
    def __init__(self, session, title, list): #@ReservedAssignment
        Screen.__init__(self, session)
        ConfigListScreen.__init__(self, [], session)
        HelpableScreen.__init__(self)
        self.skinName = "SelectSortFunctions"
        self.setTitle(title)
        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("Close"))
        self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
        {
            "cancel": (self.cancel, _("Cancel")),
        })
        self["ColorActions"] = HelpableActionMap(self, "ColorActions",
        {
            "red": (self.cancel, _("Cancel")),
            "green": (self.accept, _("Save/Close")),
        })

        l = []
        for x in list:
            l.append(getConfigListEntry(x[0], ConfigYesNo(x[1])))
        self["config"].setList(l)

    def cancel(self):
        self.close(None)

    def keyOK(self):
        self.accept()

    def accept(self):
        l = []
        for x in self["config"].getList():
            l.append(x[1].value)
        self.close(l)
