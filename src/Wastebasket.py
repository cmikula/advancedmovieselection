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
#from Plugins.Plugin import PluginDescriptor
from __init__ import _
from Screens.Screen import Screen
from Screens.InputBox import InputBox
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Components.ServicePosition import ServicePositionGauge
from Components.ActionMap import HelpableActionMap
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Components.ServiceEventTracker import ServiceEventTracker
from Components.ActionMap import ActionMap
from Components.Input import Input
from Screens.InfoBarGenerics import InfoBarSeek, InfoBarCueSheetSupport
from Components.GUIComponent import GUIComponent
from enigma import eListboxPythonMultiContent, eListbox, gFont, iPlayableService, RT_HALIGN_RIGHT, eServiceCenter, eServiceReference, getDesktop
from Screens.FixedMenu import FixedMenu
import os
from Components.config import config
from Components.Sources.StaticText import StaticText
from Components.Sources.List import List
from Components.ScrollLabel import ScrollLabel

wastelocation = config.movielist.last_videodir.value + _("Wastebasket")
lastlocation = config.movielist.last_videodir.value

class Wastebasket(Screen):
    def __init__(self, session, service, args = 0):
        Screen.__init__(self, session)
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            self.skinName = ["AdvancedMovieSelectionWastebasketHD"]
        elif sz_w == 1024:
            self.skinName = ["AdvancedMovieSelectionWastebasketXD"]
        else:
            self.skinName = ["AdvancedMovieSelectionWastebasketSD"]
        self.session = session
        self.menu = args
        list = []
        list.append((_("Empty wastebasket"), "emptywastebasket"))      
        list.append((_("Restore wastebasket"), "restorewastebasket"))
        self["menu"] = MenuList(list)
        self["wastetxt"] = StaticText("")
        self["wastelist"] = StaticText("")
        self["emptytxt"] = StaticText("")
        self["key_red"] = StaticText(_("Close"))
        self["key_green"] = StaticText(_("OK"))
        self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions"],
        {       "ok": self.go,
                "back": self.close,
                "red": self.close,
                "green": self.go,
        },-1)
        self.onShown.append(self.getList)
        self.onShown.append(self.setWindowTitle)

    def getList(self):  #todo   eine richtige liste für den papierkorb inhalt erstellen, sehe den wald vor lauter bäumen nicht :(#
        if os.path.exists(wastelocation) is True:
            for line in os.listdir(wastelocation):
                if line.endswith(".ts") is True: 
                    parts = line.rsplit(".ts",1)
                    wastelist = parts[0]
                    #print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", wastelist
                    self["wastetxt"].setText(_("Wastebasket content"))
                    self["wastelist"].setText(wastelist)

    def setWindowTitle(self):
        self.setTitle(_("Advanced Movie Selection wastebasket"))
        folder = wastelocation
        folder_size = 0
        for (path, dirs, files) in os.walk(folder):
            for file in files:
                filename = os.path.join(path, file)
                folder_size += os.path.getsize(filename)
        if folder_size == 0:
            self["wastetxt"].setText("")
            self["wastelist"].setText("")
            self["emptytxt"].setText(_("Nothing contained in the wastebasket!"))
            wastlocationtfolder = wastelocation
            if os.path.exists(wastlocationtfolder) is True:
                os.rmdir(wastlocationtfolder)
                
    def go(self):
        if os.path.exists(wastelocation) is False:
            self.session.open(MessageBox, _("Nothing to do, no wastebasket available!"), MessageBox.TYPE_INFO, timeout = 10)
            self.close()
        else:
            folder = wastelocation
            folder_size = 0
            for (path, dirs, files) in os.walk(folder):
                for file in files:
                    filename = os.path.join(path, file)
                    folder_size += os.path.getsize(filename)
            if folder_size > 1:
                returnValue = self["menu"].l.getCurrentSelection()[1]
                if returnValue is not None:
                   if returnValue is "emptywastebasket":
                      EmptyWastebasket(self.session)
                   elif returnValue is "restorewastebasket":
                      RestoreWastebasket(self.session)
            else:
                self.session.open(MessageBox, _("Nothing contained in the wastebasket!"), MessageBox.TYPE_INFO, timeout = 10)
                self.close()
                      
class EmptyWastebasket(Screen):
    def __init__(self, session):
        self.session = session
        self.session.openWithCallback(self.askForEmpty, ChoiceBox, _("Select movie to delete from wastebasket:"), self.getListWastebasket())

    def askForEmpty(self, wastebasket):
        if wastebasket is None:
           self.skipEmptyWastebasket(_("Aborted by user !!"))
        else:
           self.wastebasket = wastebasket[1]
           self.session.openWithCallback(self.EmptyWastebasketConfirmed, MessageBox, (_("Are you sure to delete %s from wastebasket?") % self.wastebasket), MessageBox.TYPE_YESNO)

    def EmptyWastebasketConfirmed(self, answer):
        if answer is None:
            self.skipEmptyWastebasket(_("Aborted by user !!"))
        if answer is False:
            self.skipEmptyWastebasket(_("User not confirming!"))
        else:
            if self.wastebasket == _("all movies"):
                for filename in os.listdir(wastelocation): 
                    wastlocationts = wastelocation + '/' + filename
                    if os.path.exists(wastlocationts) is True:
                        os.remove(wastlocationts)
                    lastlocationtsfile = lastlocation + '/' + filename + '_' + _("Wastebasket")
                    if os.path.exists(lastlocationtsfile) is True:
                        os.remove(lastlocationtsfile)
                    if filename.endswith(".ts"):
                        eitfile = filename[:-3]
                    lastlocationeitfile = lastlocation + '/' + eitfile + '.eit_' + _("Wastebasket")
                    if os.path.exists(lastlocationeitfile) is True:
                        os.remove(lastlocationeitfile)
                    if filename.endswith(".ts"):
                        jpgfile = filename[:-3]
                    lastlocationjpgfile = lastlocation + '/' + jpgfile + '.jpg_' + _("Wastebasket")
                    if os.path.exists(lastlocationjpgfile) is True:
                        os.remove(lastlocationjpgfile)
                    lastlocationapfile = lastlocation + '/' + filename + '.ap_' + _("Wastebasket")
                    if os.path.exists(lastlocationapfile) is True:
                        os.remove(lastlocationapfile)
                    lastlocationcutsfile = lastlocation + '/' + filename + '.cuts_' + _("Wastebasket")
                    if os.path.exists(lastlocationcutsfile) is True:
                        os.remove(lastlocationcutsfile)
                    lastlocationgmfile = lastlocation + '/' + filename + '.gm_' + _("Wastebasket")
                    if os.path.exists(lastlocationgmfile) is True:
                        os.remove(lastlocationgmfile)
                    lastlocationmetafile = lastlocation + '/' + filename + '.meta_' + _("Wastebasket")
                    if os.path.exists(lastlocationmetafile) is True:
                        os.remove(lastlocationmetafile)
                    lastlocationscfile = lastlocation + '/' + filename + '.sc_' + _("Wastebasket")
                    if os.path.exists(lastlocationscfile) is True:
                        os.remove(lastlocationscfile)
            else:
                for filename in os.listdir(wastelocation): 
                    if filename.startswith(self.wastebasket) is True:
                            wastlocationts = wastelocation + '/' + filename
                            if os.path.exists(wastlocationts) is True:
                                os.remove(wastlocationts)
                            lastlocationtsfile = lastlocation + '/' + filename + '_' + _("Wastebasket")
                            if os.path.exists(lastlocationtsfile) is True:
                                os.remove(lastlocationtsfile)
                            if filename.endswith(".ts"):
                                eitfile = filename[:-3]
                            lastlocationeitfile = lastlocation + '/' + eitfile + '.eit_' + _("Wastebasket")
                            if os.path.exists(lastlocationeitfile) is True:
                                os.remove(lastlocationeitfile)
                            if filename.endswith(".ts"):
                                jpgfile = filename[:-3]
                            lastlocationjpgfile = lastlocation + '/' + jpgfile + '.jpg_' + _("Wastebasket")
                            if os.path.exists(lastlocationjpgfile) is True:
                                os.remove(lastlocationjpgfile)
                            lastlocationapfile = lastlocation + '/' + filename + '.ap_' + _("Wastebasket")
                            if os.path.exists(lastlocationapfile) is True:
                                os.remove(lastlocationapfile)
                            lastlocationcutsfile = lastlocation + '/' + filename + '.cuts_' + _("Wastebasket")
                            if os.path.exists(lastlocationcutsfile) is True:
                                os.remove(lastlocationcutsfile)
                            lastlocationgmfile = lastlocation + '/' + filename + '.gm_' + _("Wastebasket")
                            if os.path.exists(lastlocationgmfile) is True:
                                os.remove(lastlocationgmfile)
                            lastlocationmetafile = lastlocation + '/' + filename + '.meta_' + _("Wastebasket")
                            if os.path.exists(lastlocationmetafile) is True:
                                os.remove(lastlocationmetafile)
                            lastlocationscfile = lastlocation + '/' + filename + '.sc_' + _("Wastebasket")
                            if os.path.exists(lastlocationscfile) is True:
                                os.remove(lastlocationscfile)
            if not self.wastebasket == _("all movies"):
                if filename.endswith(".ts"):
                    moviename = filename[:-3]
                self.session.open(MessageBox, (_("Delete %s from wastebasket completed.") % moviename), MessageBox.TYPE_INFO, timeout = 10)
            else:
                self.session.open(MessageBox, _("Empty wastebasket completed."), MessageBox.TYPE_INFO, timeout = 10)
            
    def skipEmptyWastebasket(self, reason):
        if config.AdvancedMovieSelection.showinfo.value:
            self.session.open(MessageBox, (_("Empty wastebasket was cancelled because:\n%s") % reason), MessageBox.TYPE_INFO, timeout = 10)

    def getListWastebasket(self):
        wastebasket = []
        wastebasket.append((_("All movies"), (_("all movies"))))
        parts=[]
        for line in os.listdir(wastelocation):
            if line.endswith(".ts") is True: 
                parts=line.rsplit(".ts",1)
                name=parts[0]
                wastebasket.append(( name, name ))
        return wastebasket
        
class RestoreWastebasket(Screen):
    def __init__(self, session):
        self.session = session
        self.session.openWithCallback(self.askForRestore, ChoiceBox, _("Select movies to restore from wastebasket:"), self.getListWastebasket())

    def askForRestore(self, wastebasket):
        if wastebasket is None:
           self.skipRestoreWastebasket(_("Aborted by user !!"))
        else:
           self.wastebasket = wastebasket[1]
           self.session.openWithCallback(self.RestoreWastebasketConfirmed, MessageBox, (_("Are you sure to restore %s?") % self.wastebasket), MessageBox.TYPE_YESNO)

    def RestoreWastebasketConfirmed(self, answer):
        if answer is None:
            self.skipRestoreWastebasket(_("Aborted by user !!"))
        if answer is False:
            self.skipRestoreWastebasket(_("User not confirming!"))
        else:
            if self.wastebasket == _("all movies"):
               for filename in os.listdir(wastelocation): 
                    tsfile = lastlocation + filename + _("_Wastebasket")
                    tsfilenew = lastlocation + filename
                    metafile = lastlocation + filename + '.meta' + _("_Wastebasket")
                    metafilenew = lastlocation + filename + '.meta'
                    if filename.endswith(".ts"):
                        nots = filename[:-3]
                    jpgfile = lastlocation + nots + '.jpg' + _("_Wastebasket")
                    jpgfilenew = lastlocation + nots + '.jpg'
                    eitfile = lastlocation + nots + '.eit' + _("_Wastebasket")
                    eitfilenew = lastlocation + nots + '.eit'
                    apfile = lastlocation + filename + '.ap' + _("_Wastebasket")
                    apfilenew = lastlocation + filename + '.ap'
                    cutsfile = lastlocation + filename + '.cuts' + _("_Wastebasket")
                    cutsfilenew = lastlocation + filename + '.cuts'
                    gmfile = lastlocation + filename + '.gm' + _("_Wastebasket")
                    gmfilenew = lastlocation + filename + '.gm'
                    scfile = lastlocation + filename + '.sc' + _("_Wastebasket")
                    scfilenew = lastlocation + filename + '.sc'
                    wastlocationts = wastelocation + '/' + filename
                    if os.path.exists(tsfile) is True:
                        os.rename(tsfile, tsfilenew)
                    if os.path.exists(metafile) is True:
                        os.rename(metafile, metafilenew) 
                    if os.path.exists(jpgfile) is True:
                        os.rename(jpgfile, jpgfilenew) 
                    if os.path.exists(eitfile) is True:
                        os.rename(eitfile, eitfilenew) 
                    if os.path.exists(apfile) is True:
                        os.rename(apfile, apfilenew)
                    if os.path.exists(cutsfile) is True:
                        os.rename(cutsfile, cutsfilenew) 
                    if os.path.exists(gmfile) is True:
                        os.rename(gmfile, gmfilenew) 
                    if os.path.exists(scfile) is True:
                        os.rename(scfile, scfilenew) 
                    if os.path.exists(wastlocationts) is True:
                        os.remove(wastlocationts)
            else:
                for filename in os.listdir(wastelocation): 
                    if filename.startswith(self.wastebasket) is True: 
                        tsfile = lastlocation + filename + _("_Wastebasket")
                        tsfilenew = lastlocation + filename
                        metafile = lastlocation + filename + '.meta' + _("_Wastebasket")
                        metafilenew = lastlocation + filename + '.meta'
                        if filename.endswith(".ts"):
                            nots = filename[:-3]
                        jpgfile = lastlocation + nots + '.jpg' + _("_Wastebasket")
                        jpgfilenew = lastlocation + nots + '.jpg'
                        eitfile = lastlocation + nots + '.eit' + _("_Wastebasket")
                        eitfilenew = lastlocation + nots + '.eit'
                        apfile = lastlocation + filename + '.ap' + _("_Wastebasket")
                        apfilenew = lastlocation + filename + '.ap'
                        cutsfile = lastlocation + filename + '.cuts' + _("_Wastebasket")
                        cutsfilenew = lastlocation + filename + '.cuts'
                        gmfile = lastlocation + filename + '.gm' + _("_Wastebasket")
                        gmfilenew = lastlocation + filename + '.gm'
                        scfile = lastlocation + filename + '.sc' + _("_Wastebasket")
                        scfilenew = lastlocation + filename + '.sc'
                        wastlocationts = wastelocation + '/' + filename
                        if os.path.exists(tsfile) is True:
                            os.rename(tsfile, tsfilenew)
                        if os.path.exists(metafile) is True:
                            os.rename(metafile, metafilenew) 
                        if os.path.exists(jpgfile) is True:
                            os.rename(jpgfile, jpgfilenew) 
                        if os.path.exists(eitfile) is True:
                            os.rename(eitfile, eitfilenew) 
                        if os.path.exists(apfile) is True:
                            os.rename(apfile, apfilenew)
                        if os.path.exists(cutsfile) is True:
                            os.rename(cutsfile, cutsfilenew) 
                        if os.path.exists(gmfile) is True:
                            os.rename(gmfile, gmfilenew) 
                        if os.path.exists(scfile) is True:
                            os.rename(scfile, scfilenew) 
                        if os.path.exists(wastlocationts) is True:
                            os.remove(wastlocationts) 
            if not self.wastebasket == _("all movies"):
                self.session.open(MessageBox, (_("Restore %s from wastebasket completed.") % nots), MessageBox.TYPE_INFO, timeout = 10)
            else:
                self.session.open(MessageBox, _("Restore all from wastebasket completed."), MessageBox.TYPE_INFO, timeout = 10)
                       
    def skipRestoreWastebasket(self, reason):
        if config.AdvancedMovieSelection.showinfo.value:
            self.session.open(MessageBox, (_("Restore wastebasket was cancelled because:\n%s") % reason), MessageBox.TYPE_INFO)
                
    def getListWastebasket(self):
        wastebasket = []
        wastebasket.append((_("All movies"), (_("all movies"))))
        parts=[]
        for line in os.listdir(wastelocation):
            if line.endswith(".ts") is True: 
                parts=line.rsplit(".ts",1)
                name=parts[0]
                wastebasket.append(( name, name ))
        return wastebasket
        