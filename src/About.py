#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  The plugin is developed on the basis from a lot of single plugins (thx for the code @ all)
#  Coded by JackDaniel and cmikula (c)2012
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
from Version import __version__
import AboutParser
from Components.GUIComponent import GUIComponent
from enigma import RT_HALIGN_LEFT, gFont, eListbox, eListboxPythonMultiContent, eTimer
from Components.ScrollLabel import ScrollLabel

CHANGES_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/AdvancedMovieSelection/changes_de.txt"

class AdvancedMovieSelectionVersionList(GUIComponent):
    def __init__(self):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.l.setBuildFunc(self.buildMovieSelectionListEntry)
        self.l.setFont(0, gFont("Regular", 20))                             
        self.l.setItemHeight(30)
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

    def buildMovieSelectionListEntry(self, versions, infos):
        width = self.l.getItemSize().width()
        res = [ None ]        
        res.append((eListboxPythonMultiContent.TYPE_TEXT, 5, 2, width - 30 , 23, 0, RT_HALIGN_LEFT, "%s" % versions))
        return res

    GUI_WIDGET = eListbox
    
    def postWidgetCreate(self, instance):
        instance.setContent(self.l)
        instance.selectionChanged.get().append(self.selectionChanged)

    def preWidgetRemove(self, instance):
        instance.setContent(None)
        instance.selectionChanged.get().append(self.selectionChanged)

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()
    
    def getSelectionIndex(self):
        return self.l.getCurrentSelectionIndex()

    def setList(self, list):
        self.l.setList(list)
    
    def getCurrent(self):
        return self.l.getCurrentSelection()

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
        self["version"] = StaticText(_("Version:\n") + "  " + __version__)
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

    def exit(self):
        self.close()

    def showchanges(self):
        self.session.openWithCallback(self.exit, AdvancedMovieSelectionAboutDetails)

class AdvancedMovieSelectionAboutDetails(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            self.skinName = ["AdvancedMovieSelectionAboutDetails_HD"]
        elif sz_w == 1024:
            self.skinName = ["AdvancedMovieSelectionAboutDetails_XD"]
        else:
            self.skinName = ["AdvancedMovieSelectionAboutDetails_SD"]
        self["aboutActions"] = ActionMap(["ShortcutActions", "WizardActions", "InfobarEPGActions", "EPGSelectActions"],
        {
            "red": self.exit,
            "back": self.exit,
            "nextBouquet": self.pageUp,
            "nextBouquet": self.pageUp,
            "prevBouquet": self.pageDown,
            "prevBouquet": self.pageDown,
        }, -1)
        self["key_red"] = StaticText()
        self["red"] = Pixmap()
        self["red"].hide()
        self["bouquet+"] = Pixmap()
        self["bouquet+"].hide()
        self["bouquet-"] = Pixmap()
        self["bouquet-"].hide()
        self["version_list"] = AdvancedMovieSelectionVersionList()
        self["version_list"].hide()
        self["details"] = ScrollLabel()
        self["details"].hide()
        self["waiting_txt"] = StaticText()
        self.version_timer = eTimer()
        self.version_timer.callback.append(self.parseVersion)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_("Advanced Movie Selection - History"))
        self.waiting()

    def waiting(self):
        self["waiting_txt"].setText(_("Parse changes text, please wait ..."))
        self.version_timer.start(100, True)

    def selectionChanged(self):
        self.parseInfos()
        
    def exit(self):
        self.close()

    def pageUp(self):
        self["details"].pageUp()

    def pageDown(self):
        self["details"].pageDown()
        
    def parseVersion(self):
        versions = AboutParser.parseChanges()
        versionList = []
        for version in versions:
            versions = version.getVersion()
            infos = version.getInfo()
            versionList.append((versions, infos), )
            self["waiting_txt"].setText("")
            self["bouquet+"].show()
            self["bouquet-"].show()
            self["red"].show()
            self["key_red"].setText(_("Close"))
            self["version_list"].setList(versionList)
            self["version_list"].show()                            
            if not self.selectionChanged in self["version_list"].onSelectionChanged:
                self["version_list"].onSelectionChanged.append(self.selectionChanged)
            
    def parseInfos(self):
        cur = self["version_list"].getCurrent()
        if cur is not None:
            versions = AboutParser.parseChanges()
            for version in versions:
                versions = version.getVersion()
                infos = version.getTotal()
                if infos.startswith(cur):
                    self["details"].setText(infos)
                    self["details"].show()      