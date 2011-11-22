#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  The plugin is developed on the basis from a lot of single plugins (thx for the code @ all)
#  Coded by JackDaniel @ cmikula (c)2011
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
from Components.Pixmap import Pixmap
from Components.GUIComponent import GUIComponent
from enigma import getDesktop, ePoint, eListbox
from enigma import eListboxPythonMultiContent, gFont, RT_HALIGN_LEFT, RT_VALIGN_CENTER, RT_HALIGN_CENTER
from Components.MultiContent import MultiContentEntryText
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.MenuList import MenuList
from Components.Button import Button
from Components.config import config
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import ConfigSubsection, ConfigIP, ConfigInteger, ConfigText, getConfigListEntry, configfile

def initRemoteboxEntryConfig():
    config.AdvancedMovieSelection.Entries.append(ConfigSubsection())
    i = len(config.AdvancedMovieSelection.Entries) -1
    config.AdvancedMovieSelection.Entries[i].name = ConfigText(default = "dreambox", visible_width = 50, fixed_size = False)
    config.AdvancedMovieSelection.Entries[i].ip = ConfigIP(default = [192,168,0,98])
    config.AdvancedMovieSelection.Entries[i].port = ConfigInteger(default=80, limits=(1, 65555))
    config.AdvancedMovieSelection.Entries[i].password = ConfigText(default = "dreambox", visible_width = 50, fixed_size = False)
    return config.AdvancedMovieSelection.Entries[i]

def initConfig():
    count = config.AdvancedMovieSelection.entriescount.value
    if count != 0:
        i = 0
        while i < count:
            initRemoteboxEntryConfig()
            i += 1

class AdvancedMovieSelection_RemoteboxEntrysList(MenuList):
    def __init__(self, list, enableWrapAround = True):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setFont(0, gFont("Regular", 24))
    def postWidgetCreate(self, instance):
        MenuList.postWidgetCreate(self, instance)
        instance.setItemHeight(30)

    def buildRemoteboxListEntry(self):
        self.list=[]
        for c in config.AdvancedMovieSelection.Entries:
            res = [c]
            ip = "%d.%d.%d.%d" % tuple(c.ip.value)
            port = "%d"%(c.port.value)
            try:
                sz_w = getDesktop(0).size().width()
            except:
                sz_w = 720
            if sz_w == 1280:
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 10, 0, 460, 30, 0, RT_HALIGN_LEFT|RT_VALIGN_CENTER, str(c.name.value)))
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 470, 0, 200, 30, 0, RT_HALIGN_CENTER|RT_VALIGN_CENTER, str(ip)))
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 670, 0, 100, 30, 0, RT_HALIGN_CENTER|RT_VALIGN_CENTER, str(port)))
                self.list.append(res)
            elif sz_w == 1024:
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 5, 0, 300, 30, 0, RT_HALIGN_LEFT|RT_VALIGN_CENTER, str(c.name.value)))
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 300, 0, 160, 30, 0, RT_HALIGN_CENTER|RT_VALIGN_CENTER, str(ip)))
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 515, 0, 100, 30, 0, RT_HALIGN_CENTER|RT_VALIGN_CENTER, str(port)))
                self.list.append(res)
            else:
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 0, 0, 300, 30, 0, RT_HALIGN_LEFT|RT_VALIGN_CENTER, str(c.name.value)))
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 300, 0, 150, 30, 0, RT_HALIGN_CENTER|RT_VALIGN_CENTER, str(ip)))
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 450, 0, 100, 30, 0, RT_HALIGN_CENTER|RT_VALIGN_CENTER, str(port)))
                self.list.append(res)
        self.l.setList(self.list)
        self.moveToIndex(0)

class AdvancedMovieSelection_RemoteboxEntrys(Screen):
    def __init__(self, session, what = None):
        Screen.__init__(self, session)
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            self.skinName = ["AdvancedMovieSelection_RemoteboxEntrys_HD"]
        elif sz_w == 1024:
            self.skinName = ["AdvancedMovieSelection_RemoteboxEntrys_XD"]
        else:
            self.skinName = ["AdvancedMovieSelection_RemoteboxEntrys_SD"]
        self.session = session
        self["name"] = Button(_("Name"))
        self["ip"] = Button(_("IP"))
        self["port"] = Button(_("Port"))
        self["key_red"] = Button(_("Close"))
        self["key_green"] = Button(_("Add"))
        self["key_yellow"] = Button(_("Edit"))
        self["key_blue"] = Button(_("Delete"))
        self["list"] = AdvancedMovieSelection_RemoteboxEntrysList([])
        self["actions"] = ActionMap(["WizardActions","MenuActions","ShortcutActions"],
            {
                 "ok": self.keyOK,
                 "back": self.keyClose,
                 "red": self.keyClose,
                 "green": self.keyGreen,
                 "yellow": self.keyYellow,
                 "blue": self.keyDelete,
             }, -1)
        self.onShown.append(self.setWindowTitle)
        self.what = what
        self.updateList()

    def setWindowTitle(self):
        self.setTitle(_("Advanced Movie Selection - Remotebox setup"))

    def updateList(self):
        self["list"].buildRemoteboxListEntry()

    def keyClose(self):
        self.close(self.session, self.what, None)

    def keyGreen(self):
        self.session.openWithCallback(self.updateList,AdvancedMovieSelection_RemoteboxEntryEdit,None)

    def keyOK(self):
        try:sel = self["list"].l.getCurrentSelection()[0]
        except: sel = None
        self.close(self.session, self.what, sel)

    def keyYellow(self):
        try:sel = self["list"].l.getCurrentSelection()[0]
        except: sel = None
        if sel is None:
            return
        self.session.openWithCallback(self.updateList,AdvancedMovieSelection_RemoteboxEntryEdit,sel)

    def keyDelete(self):
        try:sel = self["list"].l.getCurrentSelection()[0]
        except: sel = None
        if sel is None:
            return
        for c in config.AdvancedMovieSelection.Entries:
            name = str(c.name.value)
        self.session.openWithCallback(self.deleteConfirm, MessageBox, (_("Really delete %s entry?") % name))

    def deleteConfirm(self, result):
        if not result:
            return
        sel = self["list"].l.getCurrentSelection()[0]
        config.AdvancedMovieSelection.entriescount.value = config.AdvancedMovieSelection.entriescount.value - 1
        config.AdvancedMovieSelection.entriescount.save()
        config.AdvancedMovieSelection.Entries.remove(sel)
        config.AdvancedMovieSelection.Entries.save()
        config.AdvancedMovieSelection.save()
        configfile.save()
        self.updateList()

class AdvancedMovieSelection_RemoteboxEntryEdit(ConfigListScreen, Screen):
    def __init__(self, session, entry):
        self.session = session
        Screen.__init__(self, session)
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            self.skinName = ["AdvancedMovieSelection_RemoteboxEntryEdit_HD"]
        elif sz_w == 1024:
            self.skinName = ["AdvancedMovieSelection_RemoteboxEntryEdit_XD"]
        else:
            self.skinName = ["AdvancedMovieSelection_RemoteboxEntryEdit_SD"]
        self["actions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "green": self.keySave,
                "red": self.keyCancel,
                "blue": self.keyDelete,
                "cancel": self.keyCancel
            }, -2)
        self["HelpWindow"] = Pixmap()
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Save"))
        self["key_blue"] = Button(_("Delete"))
        if entry is None:
            self.newmode = 1
            self.current = initRemoteboxEntryConfig()
        else:
            self.newmode = 0
            self.current = entry
        self.list = [ ]
        ConfigListScreen.__init__(self, self.list, session=self.session)
        self.createSetup()
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        if self.newmode == 1:
            self.setTitle(_("Advanced Movie Selection - Remotebox new entry"))
        else:
            self.setTitle(_("Advanced Movie Selection - Remotebox edit entry"))

    def createSetup(self):
        self.list = []
        self.name = getConfigListEntry(_("Name:"), self.current.name)
        self.list.append(self.name)
        self.ip = getConfigListEntry(_("IP:"), self.current.ip)
        self.list.append(self.ip)
        self.port = getConfigListEntry(_("Port:"), self.current.port)
        self.list.append(self.port)
        self.passwd = getConfigListEntry(_("Password:"), self.current.password)
        self.list.append(self.passwd)
        self["config"].setList(self.list)
        if not self.selectionChanged in self["config"].onSelectionChanged:
            self["config"].onSelectionChanged.append(self.selectionChanged)

    def selectionChanged(self):
        current = self["config"].getCurrent()
        if current == self.name:
            self.showKeypad()
        elif current == self.ip:
            self.hideKeypad()
        elif current == self.port:
            self.hideKeypad()
        elif current == self.passwd:
            self.showKeypad()

    def keySave(self):
        if self.newmode == 1:
            config.AdvancedMovieSelection.entriescount.value = config.AdvancedMovieSelection.entriescount.value + 1
            config.AdvancedMovieSelection.entriescount.save()
        ConfigListScreen.keySave(self)
        config.AdvancedMovieSelection.save()
        configfile.save()
        self.close()

    def keyCancel(self):
        if self["config"].isChanged():
            self.hideKeypad()
            self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"))
        else:
            if self.newmode == 1:
                config.AdvancedMovieSelection.Entries.remove(self.current)
            ConfigListScreen.cancelConfirm(self, True)

    def cancelConfirm(self, result):
        if not result:
            return
        if self.newmode == 1:
            config.AdvancedMovieSelection.Entries.remove(self.current)
        ConfigListScreen.cancelConfirm(self, True)

    def keyDelete(self):
        if self.newmode == 1:
            self.keyCancel()
        else:
            self.hideKeypad()
            for x in config.AdvancedMovieSelection.Entries:
                name = str(x.name.value)
            self.session.openWithCallback(self.deleteConfirm, MessageBox, (_("Really delete %s and and all settings for?") % name))

    def showKeypad(self, retval = None):
        current = self["config"].getCurrent()
        helpwindowpos = self["HelpWindow"].getPosition()
        if hasattr(current[1], 'help_window'):
            if current[1].help_window.instance is not None:
                current[1].help_window.instance.show()
                current[1].help_window.instance.move(ePoint(helpwindowpos[0],helpwindowpos[1]))

    def hideKeypad(self):
        current = self["config"].getCurrent()
        if hasattr(current[1], 'help_window'):
            if current[1].help_window.instance is not None:
                current[1].help_window.instance.hide()

    def deleteConfirm(self, result):
        if not result:
            current = self["config"].getCurrent()
            if current == self.name:
                self.showKeypad()
            elif current == self.ip:
                self.hideKeypad()
            elif current == self.port:
                self.hideKeypad()
            elif current == self.passwd:
                self.showKeypad()
            return
        config.AdvancedMovieSelection.entriescount.value = config.AdvancedMovieSelection.entriescount.value - 1
        config.AdvancedMovieSelection.entriescount.save()
        config.AdvancedMovieSelection.Entries.remove(self.current)
        config.AdvancedMovieSelection.Entries.save()
        config.AdvancedMovieSelection.save()
        configfile.save()
        self.close()
