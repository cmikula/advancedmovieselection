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
from Screens.MessageBox import MessageBox
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from enigma import getDesktop
import os
from Components.config import config
from Components.Sources.StaticText import StaticText
import shutil
from Components.Pixmap import Pixmap

wastelocation = config.movielist.last_videodir.value + _("Wastebasket")
lastlocation = config.movielist.last_videodir.value

class Wastebasket(Screen):
    def __init__(self, session, service):
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
        self.wastelist = []
        self["wastelocation"] = StaticText()
        self["wastelist"] = MenuList(self.wastelist)
        self["wastetxt"] = StaticText("")
        self["emptytxt"] = StaticText("")
        self["key_red"] = StaticText("")
        self["key_green"] = StaticText("")
        self["key_yellow"] = StaticText("")
        self["key_blue"] = StaticText("")
        self["button_red"] = Pixmap()
        self["button_red"].hide()
        self["button_green"] = Pixmap()
        self["button_green"].hide()
        self["button_yellow"] = Pixmap()
        self["button_yellow"].hide()
        self["button_blue"] = Pixmap()
        self["button_blue"].hide()
        self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions"],
        {       "ok": self.askdelAll,
                "back": self.close,
                "red": self.askdelAll,
                "green": self.askdelSingle,
                "yellow": self.askResAll,
                "blue": self.askResSingle,
        },-1)
        self.getWasteList()
        self.onShown.append(self.setWindowTitle)

    def getWasteList(self): # todo -->  papierkorb -inhalt liste zeigt nach dem löschen/wiederherstellen einzelner filme blödsinn an, und *.meta dateien sollten auch nicht angezeigt werden :( #
        wastelocation = config.movielist.last_videodir.value + _("Wastebasket")
        if os.path.exists(wastelocation) is True:
            for line in os.listdir(wastelocation):
                movie_name_only = os.path.basename(os.path.splitext(line)[0])
                self.wastelist.append(movie_name_only.encode("utf-8"))
                self["wastelist"].l.setList(self.wastelist)
                self["wastetxt"].setText(_("Wastebasket content"))
                self["key_red"].setText(_("Delete all"))
                self["key_green"].setText(_("Delete from list"))
                self["key_yellow"].setText(_("Restore all"))
                self["key_blue"].setText(_("Restore from list"))
                self["button_red"].show()
                self["button_green"].show()
                self["button_yellow"].show()
                self["button_blue"].show()
                location = (_("Wastebasket location: %s") % config.movielist.last_videodir.value) + _("Wastebasket")
                self["wastelocation"].setText(location)
        folder = wastelocation
        folder_size = 0
        for (path, dirs, files) in os.walk(folder):
            for file in files:
                filename = os.path.join(path, file)
                folder_size += os.path.getsize(filename)
        if folder_size == 0:
            self["wastetxt"].setText("")
            if os.path.exists(wastelocation) is True:
                self["emptytxt"].setText(_("Nothing contained in the wastebasket!"))
                location = (_("Wastebasket location: %s") % config.movielist.last_videodir.value) + _("Wastebasket")
                self["wastelocation"].setText(location)
            else:
                self["emptytxt"].setText(_("Nothing to do, no wastebasket available!"))
                self["wastelocation"].setText(_("Wastebasket location: No Wastebasket available"))

    def setWindowTitle(self):
        self.setTitle(_("Advanced Movie Selection wastebasket"))

    def askdelAll(self):
        wastelocation = config.movielist.last_videodir.value + _("Wastebasket")
        if config.AdvancedMovieSelection.askdelete.value and os.path.exists(wastelocation) is True:
            self.session.openWithCallback(self.delAll, MessageBox, _("Are you sure to empty wastebasket?"), MessageBox.TYPE_YESNO)
        else:
            if os.path.exists(wastelocation) is True:
                self.delAll(True)

    def delAll(self, answer):
        if answer is None and config.AdvancedMovieSelection.showinfo.value:
            self.skipDelWastebasket(_("Aborted by user !!"))
        if answer is False and config.AdvancedMovieSelection.showinfo.value:
            self.skipDelWastebasket(_("User not confirming!"))
        else:
            wastelocation = config.movielist.last_videodir.value + _("Wastebasket")
            lastlocation = config.movielist.last_videodir.value
            try:
                for filename in os.listdir(wastelocation): 
                    wastlocationts = wastelocation + '/' + filename
                    if os.path.exists(wastlocationts) is True:
                        os.remove(wastlocationts)
                    lastlocationtsfile = lastlocation + '/' + filename + '_waste'
                    if os.path.exists(lastlocationtsfile) is True:
                        os.remove(lastlocationtsfile)
                    nots = os.path.basename(os.path.splitext(filename)[0])
                    lastlocationeitfile = lastlocation + '/' + nots + '.eit_waste'
                    if os.path.exists(lastlocationeitfile) is True:
                        os.remove(lastlocationeitfile)
                    lastlocationjpgfile = lastlocation + '/' + nots + '.jpg_waste'
                    if os.path.exists(lastlocationjpgfile) is True:
                        os.remove(lastlocationjpgfile)
                    lastlocationapfile = lastlocation + '/' + filename + '.ap_waste'
                    if os.path.exists(lastlocationapfile) is True:
                        os.remove(lastlocationapfile)
                    lastlocationcutsfile = lastlocation + '/' + filename + '.cuts_waste'
                    if os.path.exists(lastlocationcutsfile) is True:
                        os.remove(lastlocationcutsfile)
                    lastlocationgmfile = lastlocation + '/' + filename + '.gm_waste'
                    if os.path.exists(lastlocationgmfile) is True:
                        os.remove(lastlocationgmfile)
                    if not filename.endswith(".ts"):
                        lastlocationmetafile = lastlocation + '/' + filename + '.ts.meta_waste'
                    else:
                        lastlocationmetafile = lastlocation + '/' + filename + '.meta_waste'
                    if os.path.exists(lastlocationmetafile) is True:
                        os.remove(lastlocationmetafile)
                    if not filename.endswith(".ts"):
                        wastelocationmetafile = wastelocation + '/' + filename + '.ts.meta_waste'
                    else:
                        wastelocationmetafile = wastelocation + '/' + filename + '.meta_waste'
                    if os.path.exists(wastelocationmetafile) is True:
                        os.remove(wastelocationmetafile)
                    lastlocationscfile = lastlocation + '/' + filename + '.sc_waste'
                    if os.path.exists(lastlocationscfile) is True:
                        os.remove(lastlocationscfile)
                    self.getWasteList()
            except Exception, e:
                self.session.open(MessageBox, (_("Error by empty wastebasket!\n\nError message:\n%s") % str(e)), MessageBox.TYPE_ERROR)
                pass
            else:
                if config.AdvancedMovieSelection.showinfo.value:       
                    self.session.openWithCallback(self.checkFolderSize, MessageBox, _("Empty wastebasket completed."), MessageBox.TYPE_INFO, timeout = 10)
                    self.close()
                else:
                    self.checkFolderSize()

    def askdelSingle(self):
        wastelocation = config.movielist.last_videodir.value + _("Wastebasket")
        if config.AdvancedMovieSelection.askdelete.value and os.path.exists(wastelocation) is True:
            current = self["wastelist"].l.getCurrentSelection()
            moviename = os.path.basename(os.path.splitext(current)[0])
            self.session.openWithCallback(self.delSingle, MessageBox, (_("Are you sure to empty %s from wastebasket?") % moviename), MessageBox.TYPE_YESNO)
        else:
            if os.path.exists(wastelocation) is True:
                self.delSingle(True)

    def delSingle(self, answer):
        if answer is None and config.AdvancedMovieSelection.showinfo.value:
            self.skipDelWastebasket(_("Aborted by user !!"))
        if answer is False and config.AdvancedMovieSelection.showinfo.value:
            self.skipDelWastebasket(_("User not confirming!"))
        else:
            wastelocation = config.movielist.last_videodir.value + _("Wastebasket")
            lastlocation = config.movielist.last_videodir.value
            try:
                current = self["wastelist"].l.getCurrentSelection()
                for filename in os.listdir(wastelocation): 
                    if filename.startswith(current) is True:
                        wastlocationts = wastelocation + '/' + filename
                        if os.path.exists(wastlocationts) is True:
                            os.remove(wastlocationts)
                        lastlocationtsfile = lastlocation + '/' + filename + '_waste'
                        if os.path.exists(lastlocationtsfile) is True:
                            os.remove(lastlocationtsfile)
                        nots = os.path.basename(os.path.splitext(filename)[0])
                        lastlocationeitfile = lastlocation + '/' + nots + '.eit_waste'
                        if os.path.exists(lastlocationeitfile) is True:
                            os.remove(lastlocationeitfile)
                        lastlocationjpgfile = lastlocation + '/' + nots + '.jpg_waste'
                        if os.path.exists(lastlocationjpgfile) is True:
                            os.remove(lastlocationjpgfile)
                        lastlocationapfile = lastlocation + '/' + filename + '.ap_waste'
                        if os.path.exists(lastlocationapfile) is True:
                            os.remove(lastlocationapfile)
                        lastlocationcutsfile = lastlocation + '/' + filename + '.cuts_waste'
                        if os.path.exists(lastlocationcutsfile) is True:
                            os.remove(lastlocationcutsfile)
                        lastlocationgmfile = lastlocation + '/' + filename + '.gm_waste'
                        if os.path.exists(lastlocationgmfile) is True:
                            os.remove(lastlocationgmfile)
                        if not filename.endswith(".ts"):
                            lastlocationmetafile = lastlocation + '/' + filename + '.ts.meta_waste'
                        else:
                            lastlocationmetafile = lastlocation + '/' + filename + '.meta_waste'
                        if not filename.endswith(".ts"):
                            wastelocationmetafile = wastelocation + '/' + filename + '.ts.meta_waste'
                        else:
                            wastelocationmetafile = wastelocation + '/' + filename + '.meta_waste'
                        if os.path.exists(wastelocationmetafile) is True:
                            os.remove(wastelocationmetafile)
                        if os.path.exists(lastlocationmetafile) is True:
                            os.remove(lastlocationmetafile)
                        lastlocationscfile = lastlocation + '/' + filename + '.sc_waste'
                        if os.path.exists(lastlocationscfile) is True:
                            os.remove(lastlocationscfile)
                        self.getWasteList()
            except Exception, e:
                self.session.open(MessageBox, (_("Error by empty wastebasket!\n\nError message:\n%s") % str(e)), MessageBox.TYPE_ERROR)
                pass
            else: 
                if config.AdvancedMovieSelection.showinfo.value: 
                    self.session.openWithCallback(self.checkFolderSize, MessageBox, (_("Delete %s from wastebasket completed.") % nots), MessageBox.TYPE_INFO, timeout = 10)
                else:
                    self.checkFolderSize()

    def askResAll(self):
        wastelocation = config.movielist.last_videodir.value + _("Wastebasket")
        if config.AdvancedMovieSelection.askdelete.value and os.path.exists(wastelocation) is True:
            self.session.openWithCallback(self.resAll, MessageBox, _("Are you sure to restore the whole wastebasket?"), MessageBox.TYPE_YESNO)
        else:
            if os.path.exists(wastelocation) is True:
                self.resAll(True)

    def resAll(self, answer):
        if answer is None and config.AdvancedMovieSelection.showinfo.value: 
            self.skipResWastebasket(_("Aborted by user !!"))
        if answer is False and config.AdvancedMovieSelection.showinfo.value: 
            self.skipResWastebasket(_("User not confirming!"))
        else:
            try:
                wastelocation = config.movielist.last_videodir.value + _("Wastebasket")
                lastlocation = config.movielist.last_videodir.value
                for filename in os.listdir(wastelocation): 
                    tsfile = lastlocation + filename + '_waste'
                    tsfilenew = lastlocation + filename
                    if not filename.endswith(".ts"):
                        metafile = lastlocation + filename + '.ts.meta_waste'
                        metafilenew = lastlocation + filename + '.ts.meta'
                    else:
                        metafile = lastlocation + filename + '.meta_waste'
                        metafilenew = lastlocation + filename + '.meta'
                    if not filename.endswith(".ts"):
                        metafile_wastelocation = wastelocation + filename + '.ts.meta_waste'
                    else:
                        metafile_wastelocation = wastelocation + filename + '.meta_waste'
                    nots = os.path.basename(os.path.splitext(filename)[0])
                    jpgfile = lastlocation + nots + '.jpg_waste'
                    jpgfilenew = lastlocation + nots + '.jpg'
                    eitfile = lastlocation + nots + '.eit_waste'
                    eitfilenew = lastlocation + nots + '.eit'
                    apfile = lastlocation + filename + '.ap_waste'
                    apfilenew = lastlocation + filename + '.ap'
                    cutsfile = lastlocation + filename + '.cuts_waste'
                    cutsfilenew = lastlocation + filename + '.cuts'
                    gmfile = lastlocation + filename + '.gm_waste'
                    gmfilenew = lastlocation + filename + '.gm'
                    scfile = lastlocation + filename + '.sc_waste'
                    scfilenew = lastlocation + filename + '.sc'
                    wastlocationts = wastelocation + '/' + filename
                    if os.path.exists(metafile_wastelocation) is True:
                        os.remove(metafile_wastelocation) 
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
                    self.getWasteList()
            except Exception, e:
                self.session.open(MessageBox, (_("Error by restore from wastebasket!\n\nError message:\n%s") % str(e)), MessageBox.TYPE_ERROR)
                pass
            else:
                if config.AdvancedMovieSelection.showinfo.value:        
                    self.session.openWithCallback(self.checkFolderSize, MessageBox, _("Restore all from wastebasket completed."), MessageBox.TYPE_INFO, timeout = 10)
                    self.close()
                else:
                    self.checkFolderSize()

    def askResSingle(self):
        wastelocation = config.movielist.last_videodir.value + _("Wastebasket")
        if config.AdvancedMovieSelection.askdelete.value and os.path.exists(wastelocation) is True:
            current = self["wastelist"].l.getCurrentSelection()
            moviename = os.path.basename(os.path.splitext(current)[0])
            self.session.openWithCallback(self.resSingle, MessageBox, (_("Are you sure to restore %s from wastebasket?") % moviename), MessageBox.TYPE_YESNO)
        else:
            if os.path.exists(wastelocation) is True:
                self.resSingle(True)

    def resSingle(self, answer):
        if answer is None and config.AdvancedMovieSelection.showinfo.value: 
            self.skipResWastebasket(_("Aborted by user !!"))
        if answer is False and config.AdvancedMovieSelection.showinfo.value: 
            self.skipResWastebasket(_("User not confirming!"))
        else:
            try:
                wastelocation = config.movielist.last_videodir.value + _("Wastebasket")
                lastlocation = config.movielist.last_videodir.value
                current = self["wastelist"].l.getCurrentSelection()
                for filename in os.listdir(wastelocation): 
                    if filename.startswith(current) is True: 
                        tsfile = lastlocation + filename + '_waste'
                        tsfilenew = lastlocation + filename
                        if not filename.endswith(".ts"):
                            metafile = lastlocation + filename + '.ts.meta_waste'
                            metafilenew = lastlocation + filename + '.ts.meta'
                        else:
                            metafile = lastlocation + filename + '.meta_waste'
                            metafilenew = lastlocation + filename + '.meta'
                        if not filename.endswith(".ts"):
                            metafile_wastelocation = wastelocation + filename + '.ts.meta_waste'
                        else:
                            metafile_wastelocation = wastelocation + filename + '.meta_waste'
                        nots = os.path.basename(os.path.splitext(filename)[0])
                        jpgfile = lastlocation + nots + '.jpg_waste'
                        jpgfilenew = lastlocation + nots + '.jpg'
                        eitfile = lastlocation + nots + '.eit_waste'
                        eitfilenew = lastlocation + nots + '.eit'
                        apfile = lastlocation + filename + '.ap_waste'
                        apfilenew = lastlocation + filename + '.ap'
                        cutsfile = lastlocation + filename + '.cuts_waste'
                        cutsfilenew = lastlocation + filename + '.cuts'
                        gmfile = lastlocation + filename + '.gm_waste'
                        gmfilenew = lastlocation + filename + '.gm'
                        scfile = lastlocation + filename + '.sc_waste'
                        scfilenew = lastlocation + filename + '.sc'
                        wastlocationts = wastelocation + '/' + filename
                        if os.path.exists(metafile_wastelocation) is True:
                            os.remove(metafile_wastelocation) 
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
                        self.getWasteList()
            except Exception, e:
                self.session.open(MessageBox, (_("Error by restore from wastebasket!\n\nError message:\n%s") % str(e)), MessageBox.TYPE_ERROR)
                pass
            else:
                if config.AdvancedMovieSelection.showinfo.value:   
                    self.session.openWithCallback(self.checkFolderSize, MessageBox, (_("Restore %s from wastebasket completed.") % nots), MessageBox.TYPE_INFO, timeout = 10)
                else:
                    self.checkFolderSize()

    def skipDelWastebasket(self, reason):
        if config.AdvancedMovieSelection.showinfo.value:
            self.session.open(MessageBox, (_("Empty wastebasket was cancelled because:\n%s") % reason), MessageBox.TYPE_INFO, timeout = 10)

    def skipResWastebasket(self, reason):
        if config.AdvancedMovieSelection.showinfo.value:
            self.session.open(MessageBox, (_("Restore wastebasket was cancelled because:\n%s") % reason), MessageBox.TYPE_INFO, timeout = 10)

    def checkFolderSize(self, retval = None):
        wastelocation = config.movielist.last_videodir.value + _("Wastebasket")
        folder = wastelocation
        folder_size = 0
        for (path, dirs, files) in os.walk(folder):
            for file in files:
                filename = os.path.join(path, file)
                folder_size += os.path.getsize(filename)
        if folder_size == 0:
            if os.path.exists(wastelocation) is True:
                shutil.rmtree(wastelocation, ignore_errors=True, onerror=None)
                self.close()
