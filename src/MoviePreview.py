#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  The plugin is developed on the basis from a lot of single plugins (thx for the code @ all)
#  Coded by JackDaniel and cmikula (c)2011
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
from Components.AVSwitch import AVSwitch
from Components.Pixmap import Pixmap
from enigma import ePicLoad
from Tools.Directories import fileExists
import os
from Components.config import config
from ServiceProvider import eServiceReferenceDvd
from enigma import iServiceInformation, eServiceCenter
nocover = ("/usr/lib/enigma2/python/Plugins/Extensions/AdvancedMovieSelection/images/nocover.jpg")

class MoviePreview():
    def __init__(self, session):
        self.onHide.append(self.hideDialog)
        self["CoverPreview"] = Pixmap()
        self.working = False
        self.picParam = None
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.showPreviewCallback)
        self.onLayoutFinish.append(self.layoutFinish)

    def layoutFinish(self):
        sc = AVSwitch().getFramebufferScale()
        self.picload.setPara((self["CoverPreview"].instance.size().width(), self["CoverPreview"].instance.size().height(), sc[0], sc[1], False, 1, "#00000000"))
        self.cpX = self["CoverPreview"].instance.position().x()
        self.cpY = self["CoverPreview"].instance.position().y()
        self.cpW = self["CoverPreview"].instance.size().width()
        self.cpH = self["CoverPreview"].instance.size().height()
        self.piconX = self.cpX + int(self.cpW / 2) - int(100 / 2)
        self.piconY = self.cpY + int(self.cpH / 2) - int(60 / 2)

    def getServiceInfoValue(self, ref, what):
        info = eServiceCenter.getInstance().info(ref)
        v = ref and info.getInfo(ref, what) or info.getInfo(what)
        if v != iServiceInformation.resIsString:
            return ""
        return ref and info.getInfoString(ref, what) or info.getInfoString(what)

    def loadPreview(self, serviceref):
        self.hideDialog()
        if serviceref:
            path = serviceref.getPath()
            if os.path.isfile(path):
                path = os.path.splitext(path)[0] + ".jpg"
            elif isinstance(serviceref, eServiceReferenceDvd):
                path = path + ".jpg"
            elif config.AdvancedMovieSelection.usefoldername.value:
                if path.endswith("/"):
                    path = path[:-1] + ".jpg"
            else:
                path = path + "folder.jpg"
        
            self.working = True
            self["CoverPreview"].setPosition(self.cpX, self.cpY)
            if fileExists(path):
                self.picload.startDecode(path)
            elif serviceref.getPath().endswith(".ts") and config.AdvancedMovieSelection.show_picon.value:
                picon = self.getServiceInfoValue(serviceref, iServiceInformation.sServiceref).rstrip(':').replace(':', '_') + ".png"
                piconpath = os.path.join(config.AdvancedMovieSelection.piconpath.value, picon)
                if os.path.exists(piconpath):
                    if config.AdvancedMovieSelection.piconsize.value:
                        self["CoverPreview"].instance.setPixmapFromFile(piconpath)
                        self["CoverPreview"].setPosition(self.piconX, self.piconY)
                    else:
                        self.picload.startDecode(piconpath)
                else:
                    self.picload.startDecode(nocover)
            else:
                self.picload.startDecode(nocover)
                
    def showPreviewCallback(self, picInfo=None):
        if picInfo and self.working:
            ptr = self.picload.getData()
            if ptr != None:
                self["CoverPreview"].instance.setPixmap(ptr)
        self.working = False

    def hideDialog(self):
        self.working = False
