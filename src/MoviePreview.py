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
from enigma import gPixmapPtr
from Source.Timer import xTimer
from Tools.Directories import fileExists
import os
from Components.config import config
from Source.ServiceProvider import eServiceReferenceDvd, getServiceInfoValue, ServiceCenter, eServiceReferenceBludisc
from Source.ISOInfo import ISOInfo
from Source.PicLoader import PicLoader
from enigma import iServiceInformation, eServiceReference
from Source.Globals import getNocover

class MoviePreview():
    def __init__(self, session):
        self.onHide.append(self.hideDialog)
        self["CoverPreview"] = Pixmap()
        self["backdrop"] = Pixmap()
        self.old_service = None
        self.working = False
        self.picParam = None
        self.picload = PicLoader()
        self.picload.addCallback(self.showPreviewCallback)
        self.backdrop = PicLoader()
        self.backdrop.addCallback(self.showBackdropCallback)
        self.onLayoutFinish.append(self.layoutFinish)
        self.onClose.append(self.__onClose)

    def __onClose(self):
        self.picload.destroy()
        self.backdrop.destroy()
    
    def layoutFinish(self):
        sc = AVSwitch().getFramebufferScale()
        self.picload.setPara((self["CoverPreview"].instance.size().width(), self["CoverPreview"].instance.size().height(), sc[0], sc[1], False, 1, "#ff000000"))
        self.backdrop.setPara((self["backdrop"].instance.size().width(), self["backdrop"].instance.size().height(), sc[0], sc[1], False, 1, "#ff000000"))

    def loadPreview(self, serviceref):
        self.hideDialog()
        if serviceref is None:
            empty = gPixmapPtr()
            self["CoverPreview"].instance.setPixmap(empty)
            self["backdrop"].hide()
            return
        path = serviceref.getPath()
        if serviceref.flags & eServiceReference.mustDescent:
            # directory
            if fileExists(path + ".jpg"):
                path += ".jpg"
            elif config.AdvancedMovieSelection.usefoldername.value:
                path = path[:-1] + ".jpg"
            else:
                path = path + "folder.jpg"
        elif os.path.isfile(path):
            # file service
            path_s = os.path.splitext(path)[0]
            path = path_s + ".jpg"
        else:   
            # structure service
            path = path + ".jpg"
        
        # load cover or provider icon
        self.working = True
        if fileExists(path):
            self.picload.startDecode(path)
            return
        series_path = os.path.join(os.path.dirname(path), "series.jpg")
        if fileExists(series_path):
            self.picload.startDecode(series_path)
            return
        # cover for serienrecorder plugin
        dir_name = os.path.dirname(path)
        series_path = os.path.join(dir_name,  os.path.basename(dir_name) + ".jpg")
        if fileExists(series_path):
            self.picload.startDecode(series_path)
            return
        if serviceref.getPath().endswith(".ts") and config.AdvancedMovieSelection.show_picon.value:
            picon = getServiceInfoValue(serviceref, iServiceInformation.sServiceref).rstrip(':').replace(':', '_') + ".png"
            piconpath = os.path.join(config.AdvancedMovieSelection.piconpath.value, picon)
            if fileExists(piconpath):
                self.picload.startDecode(piconpath)
                return
        cover_path = os.path.join(os.path.dirname(path), "cover.jpg")
        if fileExists(cover_path):
            self.picload.startDecode(cover_path)
        else:
            self.picload.startDecode(getNocover())
    
    def loadBackdrop(self, serviceref):
        self.backdrop_load = False
        if serviceref is None or not config.AdvancedMovieSelection.show_backdrop.value:
            self["backdrop"].hide()
            return

        if serviceref.flags & eServiceReference.mustDescent:
            backdrop_file = os.path.join(os.path.dirname(serviceref.getPath()), ".backdrop.jpg")
            if fileExists(backdrop_file):
                self.backdrop_load = True
                self.backdrop.startDecode(backdrop_file)
            else:
                self["backdrop"].hide()
            return
        
        path = serviceref.getPath()
        if os.path.isfile(path):
            # file service
            path_s = os.path.splitext(path)[0]
            backdrop_file = path_s + ".backdrop.jpg"
        else:
            # structure service
            backdrop_file = path + ".backdrop.jpg"
        
        # load backdrop
        if backdrop_file is not None and fileExists(backdrop_file):
            self.backdrop_load = True
            self.backdrop.startDecode(backdrop_file)
            return
        backdrop_file = os.path.join(os.path.dirname(path), "backdrop.jpg")
        if fileExists(backdrop_file):
            self.backdrop_load = True
            self.backdrop.startDecode(backdrop_file)
        else:
            self["backdrop"].hide()

    def showPreviewCallback(self, picInfo=None):
        if picInfo:
            ptr = self.picload.getData()
            if ptr != None and self.working:
                self["CoverPreview"].instance.setPixmap(ptr)
        self.working = False

    def showBackdropCallback(self, picInfo=None):
        if picInfo:
            ptr = self.backdrop.getData()
            if ptr != None and self.backdrop_load:
                self["backdrop"].instance.setPixmap(ptr)
                self["backdrop"].show()
        self.backdrop_load = False

    def hideDialog(self):
        self.working = False

from Screens.Screen import Screen
from enigma import getDesktop
class DVDOverlay(Screen):
    def __init__(self, session, args = None):
        desktop_size = getDesktop(0).size()
        DVDOverlay.skin = """<screen name="DVDOverlay" position="0,0" size="%d,%d" flags="wfNoBorder" zPosition="-1" backgroundColor="transparent" />""" %(desktop_size.width(), desktop_size.height())
        Screen.__init__(self, session)

from ServiceReference import ServiceReference
from Screens.InfoBarGenerics import InfoBarCueSheetSupport
from Source.ServiceProvider import CueSheet
class VideoPreview():
    def __init__(self):
        self.fwd_timer = xTimer()
        self.fwd_timer.addCallback(self.fwd)
        self.dvd_preview_timer = xTimer()
        self.dvd_preview_timer.addCallback(self.playLastDVD)
        self.video_preview_timer = xTimer()
        self.video_preview_timer.addCallback(self.playMovie)
        self.service = None
        self.currentlyPlayingService = None
        self.cut_list = None
        self.lastService = None
        self.updateVideoPreviewSettings()
        self.onClose.append(self.__playLastService)
        self.dvdScreen = self.session.instantiateDialog(DVDOverlay)
        
    def updateVideoPreviewSettings(self):
        self.enabled = config.AdvancedMovieSelection.video_preview.value
        if not self.enabled:
            self.__playLastService()

    def stopCurrentlyPlayingService(self):
        if self.currentlyPlayingService:
            if isinstance(self.currentlyPlayingService, eServiceReferenceDvd):
                subs = self.getServiceInterface("subtitle")
                if subs:
                    subs.disableSubtitles(self.session.current_dialog.instance)
            self.session.nav.stopService()
            cue = CueSheet(self.currentlyPlayingService)
            cue.setCutList(self.cut_list)
            self.currentlyPlayingService = None

    def setNewCutList(self, cut_list):
        self.cut_list = cut_list
        
    def jumpForward(self):
        return self.seekRelativ(config.AdvancedMovieSelection.video_preview_jump_time.value)
    
    def jumpBackward(self):
        jumptime = config.AdvancedMovieSelection.video_preview_jump_time.value
        return self.seekRelativ(-jumptime)

    def togglePreviewStatus(self, service=None):
        self.enabled = not self.enabled
        if not self.currentlyPlayingService:
            self.enabled = True
        self.__playLastService()
        if self.enabled and service:
            self.service = service
            self.playMovie()

    def seekRelativ(self, minutes):
        if self.currentlyPlayingService:
            self.doSeekRelative(minutes * 60 * 90000)
            return True

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
            if self.service.flags & eServiceReference.mustDescent or isinstance(self.service, eServiceReferenceBludisc):
                print "Skipping video preview"
                self.__playLastService()
                return
            from MoviePlayer import playerChoice
            if playerChoice and playerChoice.isPlaying():
                print "Skipping video preview"
                return
            cpsr = self.session.nav.getCurrentlyPlayingServiceReference()
            if cpsr and cpsr == self.service:
                return 
            if self.lastService is None:
                self.lastService = self.session.nav.getCurrentlyPlayingServiceReference()
            self.stopCurrentlyPlayingService()
            if isinstance(self.service, eServiceReferenceDvd):
                if self.service.isIsoImage():
                    if ISOInfo().getFormatISO9660(self.service) != ISOInfo.DVD:
                        print "Skipping video preview"
                        self.__playLastService()
                        return
                newref = eServiceReference(4369, 0, self.service.getPath())
                self.session.nav.playService(newref)
                subs = self.getServiceInterface("subtitle")
                if subs:
                    subs.enableSubtitles(self.dvdScreen.instance, None)
            else:
                self.session.nav.playService(self.service)
            print "play", self.service.getPath()
            self.currentlyPlayingService = self.service
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
                            self.minutes = long(last / 90000 / 60)
                            if isinstance(self.service, eServiceReferenceDvd):
                                self.resume_point = last
                                self.dvd_preview_timer.start(1000, True)
                                return
                            self.fwd_timer.start(1000, True)
                except Exception, e:
                    print e

    def fwd(self):
        self.seekRelativ(self.minutes)

    def getServiceInterface(self, iface):
        service = self.session.nav.getCurrentService()
        if service:
            attr = getattr(service, iface, None)
            if callable(attr):
                return attr()
        return None
            
    def playLastDVD(self, answer=True):
        print "playLastDVD", self.resume_point
        service = self.session.nav.getCurrentService()
        if service:
            if answer == True:
                seekable = self.getSeek()
                if seekable:
                    seekable.seekTo(self.resume_point)
            pause = service.pause()
            pause.unpause()

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

    def getCurrentlyPlayingService(self):
        return self.currentlyPlayingService

    def __playLastService(self):
        self.stopCurrentlyPlayingService()
        if self.lastService:
            self.session.nav.playService(self.lastService)
