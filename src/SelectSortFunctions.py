#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Copyright (C) 2014 cmikula

SelectSortFunctions for Advanced Movie Selection

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
from Components.config import config, getConfigListEntry, ConfigYesNo

class SelectSortFunctions(ConfigListScreen, Screen, HelpableScreen):
    def __init__(self, session, title, item_descr, selected_items):
        Screen.__init__(self, session)
        ConfigListScreen.__init__(self, [], session)
        HelpableScreen.__init__(self)
        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("Save/Close"))
        sels = config.AdvancedMovieSelection.sort_functions.value.split()
        from MovieList import MovieList
        self.conf1 = ConfigYesNo(str(MovieList.SORT_ALPHANUMERIC) in sels)
        self.conf2 = ConfigYesNo(str(MovieList.SORT_DATE_ASC) in sels)
        self.conf3 = ConfigYesNo(str(MovieList.SORT_DATE_DESC) in sels)
        self.conf4 = ConfigYesNo(str(MovieList.SORT_DESCRIPTION) in sels)
        self["config"].setList([
            getConfigListEntry(_("Alphabetic sort"), self.conf1),
            getConfigListEntry(_("Sort by date (ascending)"), self.conf2),
            getConfigListEntry(_("Sort by date (descending)"), self.conf3),
            getConfigListEntry(_("Sort by description"), self.conf4)
        ])

        self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
        {
            "cancel": (self.cancel, _("Cancel")),
        })
        self["ColorActions"] = HelpableActionMap(self, "ColorActions",
        {
            "red": (self.cancel, _("Cancel")),
            "green": (self.accept, _("Save/Close"))
        })
        self.setTitle(title)

    def cancel(self):
        self.close(None)

    def accept(self):
        from MovieList import MovieList
        l = []
        if self.conf1.value:
            l.append(str(MovieList.SORT_ALPHANUMERIC))
        if self.conf2.value:
            l.append(str(MovieList.SORT_DATE_ASC))
        if self.conf3.value:
            l.append(str(MovieList.SORT_DATE_DESC))
        if self.conf4.value:
            l.append(str(MovieList.SORT_DESCRIPTION))
        self.close(l)
