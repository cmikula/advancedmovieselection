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
from Screens.Screen import Screen
from Components.AVSwitch import AVSwitch
from Components.Pixmap import Pixmap
from Components.Label import Label
from enigma import ePicLoad
from Tools.Directories import fileExists
from enigma import getDesktop
import os
from Components.config import config
from ServiceProvider import eServiceReferenceDvd
#from skin import loadSkin
#loadSkin("/usr/lib/enigma2/python/Plugins/Extensions/AdvancedMovieSelection/skin/skin.xml")

nocover = ("/usr/lib/enigma2/python/Plugins/Extensions/AdvancedMovieSelection/images/nocover.jpg")

class MovielistPreview(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        if config.AdvancedMovieSelection.showpreview.value and config.AdvancedMovieSelection.minitv.value:
            try:
                sz_w = getDesktop(0).size().width()
            except:
                sz_w = 720
            if sz_w == 1280:
                self.skinName = ["AdvancedMovieSelectionCoverHD"]
            elif sz_w == 1024:
                self.skinName = ["AdvancedMovieSelectionCoverXD"]
            else:
                self.skinName = ["AdvancedMovieSelectionCoverSD"]
        if config.AdvancedMovieSelection.showpreview.value and not config.AdvancedMovieSelection.minitv.value:
            try:
                sz_w = getDesktop(0).size().width()
            except:
                sz_w = 720
            if sz_w == 1280:
                self.skinName = ["AdvancedMovieSelectionCover_noMiniTV_HD"]
            elif sz_w == 1024:
                self.skinName = ["AdvancedMovieSelectionCover_noMiniTV_XD"]
            else:
                self.skinName = ["AdvancedMovieSelectionCover_noMiniTV_SD"]        
        self["background"] = Label("")
        self["preview"] = Pixmap()
            
class MoviePreview():
    def __init__(self, session):
        self.dialog = session.instantiateDialog(MovielistPreview)
        self.onHide.append(self.hideDialog)
        self.working = False
        self.picParam = None

    def loadPreview(self, serviceref):
        self.hideDialog()
        if serviceref:
            path = serviceref.getPath()
            print "Preview " + path
            # DVD directory
            if os.path.isfile(path):
                path = os.path.splitext(path)[0] + ".jpg"
                print "Preview 1" + path
            elif isinstance(serviceref, eServiceReferenceDvd):
                path = path + ".jpg"
                print "Preview 2" + path
            else:
                path = path + "folder.jpg"
                print "Preview 3" + path
            
            if fileExists(path):
                self.showDialog()
                self.working = True
                sc = AVSwitch().getFramebufferScale()
                self.picload = ePicLoad()
                self.picload.PictureData.get().append(self.showPreviewCallback)
                self.picload.setPara((self.dialog["preview"].instance.size().width(), self.dialog["preview"].instance.size().height(), sc[0], sc[1], False, 1, "#00000000"))
                self.dialog.hide()
                self.picload.startDecode(path)
            else:
                self.showDialog()
                self.working = True
                sc = AVSwitch().getFramebufferScale()
                self.picload = ePicLoad()
                self.picload.PictureData.get().append(self.showPreviewCallback)
                self.picload.setPara((self.dialog["preview"].instance.size().width(), self.dialog["preview"].instance.size().height(), sc[0], sc[1], False, 1, "#00000000"))
                self.dialog.hide()
                self.picload.startDecode(nocover)
            
    def showPreviewCallback(self, picInfo=None):
        if picInfo and self.working:
            ptr = self.picload.getData()
            if ptr != None:
                self.dialog["preview"].instance.setPixmap(ptr)
                self.dialog.show()
        self.working = False

    def hideDialog(self):
        self.working = False
        self.dialog.hide()

    def showDialog(self):
        self.dialog.show()
        
