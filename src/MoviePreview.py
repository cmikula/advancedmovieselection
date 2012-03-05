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
from enigma import ePicLoad, eTimer
from Tools.Directories import fileExists
import os
from Components.config import config
from ServiceProvider import eServiceReferenceDvd, getServiceInfoValue, ServiceCenter
from enigma import iServiceInformation, eServiceReference
from os import environ

nocover = None

class MoviePreview():
    def __init__(self, session):
        self.onHide.append(self.hideDialog)
        self["CoverPreview"] = Pixmap()
        self.old_service = None
        self.working = False
        self.picParam = None
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.showPreviewCallback)
        self.onLayoutFinish.append(self.layoutFinish)
        global nocover
        if environ["LANGUAGE"] == "de" or environ["LANGUAGE"] == "de_DE":
            nocover = ("/usr/lib/enigma2/python/Plugins/Extensions/AdvancedMovieSelection/images/nocover_de.png")
        else:
            nocover = ("/usr/lib/enigma2/python/Plugins/Extensions/AdvancedMovieSelection/images/nocover_en.png")

    def layoutFinish(self):
        sc = AVSwitch().getFramebufferScale()
        self.picload.setPara((self["CoverPreview"].instance.size().width(), self["CoverPreview"].instance.size().height(), sc[0], sc[1], False, 1, "#00000000"))
        self.cpX = self["CoverPreview"].instance.position().x()
        self.cpY = self["CoverPreview"].instance.position().y()
        self.cpW = self["CoverPreview"].instance.size().width()
        self.cpH = self["CoverPreview"].instance.size().height()
        self.piconX = self.cpX + int(self.cpW / 2) - int(100 / 2)
        self.piconY = self.cpY + int(self.cpH / 2) - int(60 / 2)

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
                return
            series_path = os.path.join(os.path.dirname(path), "series.jpg")
            if os.path.exists(series_path):
                self.picload.startDecode(series_path)
                return
            if serviceref.getPath().endswith(".ts") and config.AdvancedMovieSelection.show_picon.value:
                picon = getServiceInfoValue(serviceref, iServiceInformation.sServiceref).rstrip(':').replace(':', '_') + ".png"
                piconpath = os.path.join(config.AdvancedMovieSelection.piconpath.value, picon)
                if os.path.exists(piconpath):
                    if config.AdvancedMovieSelection.piconsize.value:
                        self["CoverPreview"].instance.setPixmapFromFile(piconpath)
                        self["CoverPreview"].setPosition(self.piconX, self.piconY)
                    else:
                        self.picload.startDecode(piconpath)
                return
            self.picload.startDecode(nocover)
                
    def showPreviewCallback(self, picInfo=None):
        if picInfo and self.working:
            ptr = self.picload.getData()
            if ptr != None:
                self["CoverPreview"].instance.setPixmap(ptr)
        self.working = False

    def hideDialog(self):
        self.working = False


from ServiceReference import ServiceReference
from Screens.InfoBarGenerics import InfoBarCueSheetSupport
from ServiceProvider import CueSheet
class VideoPreview():
    def __init__(self):
        self.fwd_timer = eTimer()
        self.fwd_timer.timeout.get().append(self.fwd)
        self.video_preview_timer = eTimer()
        self.video_preview_timer.timeout.get().append(self.playMovie)
        self.lastService = None
        self.service = None
        self.currentlyPlayingService = None
        self.cut_list = None
        self.enabled = config.AdvancedMovieSelection.video_preview.value
        self.onClose.append(self.__playLastService)

    def stopCurrentlyPlayingService(self):
        if self.currentlyPlayingService:
            self.session.nav.stopService()
            cue = CueSheet(self.currentlyPlayingService)
            cue.setCutList(self.cut_list)
            self.currentlyPlayingService = None

    def setNewCutList(self, cut_list):
        self.cut_list = cut_list
        
    def jumpForward(self):
        self.seekRelativ(config.AdvancedMovieSelection.video_preview_jump_time.value)
    
    def jumpBackward(self):
        jumptime = '-' + str(config.AdvancedMovieSelection.video_preview_jump_time.value)
        self.seekRelativ(int(jumptime))

    def togglePreviewStatus(self, service=None):
        self.__playLastService()
        self.enabled = not self.enabled
        if self.enabled and service:
            self.service = service
            self.playMovie()

    def seekRelativ(self, minutes):
        if self.currentlyPlayingService:
            self.doSeekRelative(minutes * 60 * 90000)

    def getSeek(self):
        service = self.session.nav.getCurrentService()
        if service is None:
            return None
        seek = service.seek()
        if seek is None or not seek.isCurrentlySeekable():
            return None
        return seek
    
    def doSeekRelative(self, pts):
        seekable = self.getSeek()
        if seekable is None:
            return
        seekable.seekRelative(pts < 0 and -1 or 1, abs(pts))

    def playMovie(self):
        if self.service and self.enabled:
            print "play service"
            if isinstance(self.service, eServiceReferenceDvd) or self.service.flags & eServiceReference.mustDescent:
                print "Skipping video preview"
                self.__playLastService()
                return
            from plugin import PlayerInstance
            if PlayerInstance:
                return
            if self.session.nav.getCurrentlyPlayingServiceReference() == self.service:
                return 
            if not self.lastService:
                self.lastService = self.session.nav.getCurrentlyPlayingServiceReference()
            if self.currentlyPlayingService:
                self.stopCurrentlyPlayingService()
            self.currentlyPlayingService = self.service
            self.session.nav.playService(self.service)
            seekable = self.getSeek()
            if seekable:
                try:
                    cue = CueSheet(self.service)
                    self.cut_list = cue.getCutList()
                    length, last = self.getCuePositions()
                    stop_before_end_time = int(config.AdvancedMovieSelection.stop_before_end_time.value)
                    if stop_before_end_time > 0:
                        if (((length) - (last / 90000)) / 60) < stop_before_end_time:
                            return
                    if last > 0 and config.AdvancedMovieSelection.video_preview_marker.value:
                        if self.service.getPath().endswith('ts'):
                            seekable.seekTo(last)
                        else:
                            self.fwd_timer.start(500, True)
                            self.minutes = last / 90000 / 60
                except Exception, e:
                    print e

    def fwd(self):
        self.seekRelativ(self.minutes)
            
    def preparePlayMovie(self, service, event):
        if not self.execing or not self.enabled:
            return
        self.service = service
        if service:
            serviceHandler = ServiceCenter.getInstance()
            info = serviceHandler.info(self.service)
            service = ServiceReference(info.getInfoString(self.service, iServiceInformation.sServiceref))
            self.video_preview_timer.start(config.AdvancedMovieSelection.video_preview_delay.value * 1000, True)

    def getCuePositions(self):
        length = 0
        last_pos = 0
        for (pts, what) in self.cut_list:
            if what == 1 == InfoBarCueSheetSupport.CUT_TYPE_OUT:
                length = pts / 90000
            elif what == InfoBarCueSheetSupport.CUT_TYPE_LAST:
                last_pos = pts
        if length == 0:
            info = ServiceCenter.getInstance().info(self.currentlyPlayingService)
            if info:
                length = info.getLength(self.currentlyPlayingService)
        return [length, last_pos]

    def getCurrentlyPlayingSerice(self):
        return self.currentlyPlayingService

    def __playLastService(self):
        if self.lastService:
            self.stopCurrentlyPlayingService()
            self.session.nav.playService(self.lastService)
            self.lastService = None
