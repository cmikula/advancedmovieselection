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
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.Button import Button
from Components.Sources.StaticText import StaticText
from Components.config import config, getConfigListEntry
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from MessageSocket import instance as messageServer, getIpAddress
from enigma import getDesktop
from Components.GUIComponent import GUIComponent
from enigma import eListboxPythonMultiContent, eListbox, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT
from Components.MultiContent import MultiContentEntryText

staticIP = None

class ClientSetupList(GUIComponent):
    def __init__(self):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()        
        self.l.setFont(0, gFont("Regular", 22))
        self.l.setFont(1, gFont("Regular", 18))
        self.l.setItemHeight(50)
        self.l.setBuildFunc(self.buildMovieListEntry)
        
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

    def buildMovieListEntry(self, serviceref, info, begin, length):
        res = [ None ]
        width = self.l.getItemSize().width()
        width_up_r = 250
        width_up_l = width - width_up_r
        width_dn_r = width / 2
        width_dn_l = width - width_dn_r
        pos_up_r = width - width_up_r 
        pos_dn_r = width - width_dn_r
        return res

    def moveToIndex(self, index):
        self.instance.moveSelectionTo(index)

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()

    def getCurrent(self):
        l = self.l.getCurrentSelection()
        return l and l[0]

    GUI_WIDGET = eListbox

    def load(self, root):
        self.list = [ ]
        return

    def reload(self):
        self.load()
        self.l.setList(self.list)

class AdvancedMovieSelection_ClientSetup(ConfigListScreen, Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            self.skinName = ["AdvancedMovieSelection_ClientSetup_HD"]
        elif sz_w == 1024:
            self.skinName = ["AdvancedMovieSelection_ClientSetup_XD"]
        else:
            self.skinName = ["AdvancedMovieSelection_ClientSetup_SD"]
        self.session = session
        self["key_red"] = Button(_("Close"))
        self["key_green"] = StaticText("")
        self["key_yellow"] = StaticText("")
        self["actions"] = ActionMap(["WizardActions","MenuActions","ShortcutActions"],
            {
                 "ok": self.keySave,
                 "back": self.keyCancel,
                 "red": self.keyCancel,
                 "green": self.keySave,
                 "yellow": self.keyYellow,
             }, -1)
        self["status"] = StaticText("")
        self["help"] = StaticText("")
        self["clientlist"] = StaticText("")
        self["green_button"] = Pixmap()
        self["yellow_button"] = Pixmap()
        self["green_button"].hide()
        self["yellow_button"].hide()
        self.list = [ ]
        ConfigListScreen.__init__(self, self.list, session=self.session)
        if not self.showHelp in self["config"].onSelectionChanged:
            self["config"].onSelectionChanged.append(self.showHelp)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        clients = messageServer.getClients()
        self.setTitle(_("Advanced Movie Selection - Clientbox setup"))  
        staticIP = getIpAddress('eth0')
        if staticIP is not None:
            staticIP = True       
            self.createSetup()
            self["key_green"].setText(_("Save"))
            self["key_yellow"].setText(_("Manuall rescan"))
            self["green_button"].show()
            self["yellow_button"].show()
            self["clientlist"].setText(_("Detected clients: %s") % clients)
        else:
            self["status"].setText(_("ATTENTION: DHCP in lan configuration is activ, no clientbox services available!"))
         
    def createSetup(self):
        self.list = []
        self.list.append(getConfigListEntry(_("Start search IP:"), config.AdvancedMovieSelection.start_search_ip, _("only last three digits")))
        self.list.append(getConfigListEntry(_("Stop search IP:"), config.AdvancedMovieSelection.stop_search_ip, _("only last three digits")))
        self["config"].setList(self.list)

    def showHelp(self):
        current = self["config"].getCurrent()
        if len(current) > 2 and current[2] is not None:
            self["help"].setText(current[2])
        else:
            self["help"].setText(_("No Helptext available!"))

    def cancelConfirm(self, result):
        if not result:
            return
        for x in self["config"].list:
            x[1].cancel()
        self.close()

    def keyCancel(self):
        if self["config"].isChanged():
            self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"))
        else:
            self.close()
            
    def keySave(self):
        if staticIP == True:
            ConfigListScreen.keySave(self)
        
    def keyYellow(self):
        if staticIP == True:
            messageServer.startScanForClients()
        