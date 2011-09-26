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
from Components.Sources.StaticText import StaticText
from Screens.Console import Console
from Tools.Directories import fileExists
from Components.Pixmap import Pixmap
from Components.ActionMap import ActionMap
from enigma import getDesktop

changestxt = "/usr/lib/enigma2/python/Plugins/Extensions/AdvancedMovieSelection/changes_de.txt"

class AdvancedMovieSelectionAbout(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            self.skinName = ["AdvancedMovieSelectionAboutHD"]
        elif sz_w == 1024:
            self.skinName = ["AdvancedMovieSelectionAboutXD"]
        else:
            self.skinName = ["AdvancedMovieSelectionAboutSD"]
        self["aboutActions"] = ActionMap(["ShortcutActions", "WizardActions", "InfobarEPGActions"],
        {
            "red": self.exit,
            "green": self.showchanges,
            "back": self.exit,
            "ok": self.exit,
        }, -1)
        self["version"] = StaticText(_("Version:\n") + '  1.9')
        self["author"] = StaticText(_("Developer:\n  JackDaniel, cmikula"))
        self["translation"] = StaticText(_("Thanks for translation to:\n") + '  nl=Bschaar')
        self["license"] = StaticText(_("This plugin may only executed on hardware which is licensed by Dream Multimedia GmbH."))
        self["thanks"] = StaticText(_("Thanks to all other for help and so many very good code."))
        self["key_red"] = StaticText(_("Close"))
        self["key_green"] = StaticText(_("Show changes"))
        self["red"] = Pixmap()
        self["green"] = Pixmap()
        self.onLayoutFinish.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_("About Advanced Movie Selection"))

    def showchanges(self):
        if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/AdvancedMovieSelection/changes_de.txt"):
            self.session.open(Console, title=_("Advanced Movie Selection - History"), cmdlist=["cat %s" % changestxt])
        else:
            pass

    def exit(self):
        self.close()
