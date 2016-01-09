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
from Screens.MessageBox import MessageBox
from Components.Label import Label
from Components.Button import Button
from Components.Pixmap import Pixmap
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from threading import Thread
from enigma import eServiceReference
from timer import eTimer
from Components.MenuList import MenuList
from Source.ServiceProvider import ServiceCenter
from Source.EITTools import createEIT
from Source.MovieDB import tmdb, downloadCover
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ScrollLabel import ScrollLabel
from Source.Globals import printStackTrace
from Source.PicLoader import PicLoader
from Source.Globals import getIconPath
import os

fetchingMovies = None

class DownloadMovies(Screen):
    def __init__(self, session, items, service=None):
        Screen.__init__(self, session)
        self.skinName = "AdvancedMovieSelectionDownload"
        self.onShow.append(self.selectionChanged)
        self.onClose.append(self.__onClose)
        self.service = service
        self["logo"] = Pixmap()  
        self["info"] = Label()
        self["title"] = Label()
        self["poster"] = Pixmap()
        self["poster"].hide()
        self["description"] = ScrollLabel()
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button("")
        self["key_yellow"] = Button("")
        self["key_yellow"] = Label(_("Manual search"))
        if service is not None:
            self["key_green"] = Label(_("Save infos/cover"))
        else:
            self["key_green"] = Label(_("Background"))
            self["key_yellow"].hide()

        self["ActionsMap"] = ActionMap(["SetupActions", "ColorActions"],
         {
          "ok": self.titleSelected,
          "green": self.titleSelected,
          "red": self.__cancel,
          "yellow": self.editTitle,
          "cancel": self.__cancel,
          "left": self.scrollLabelPageUp,
          "right": self.scrollLabelPageDown
          }, -1)
        self.onShown.append(self.setWindowTitle)
      
        self.l = []
        self["list"] = MenuList(self.l)
        self["list"].onSelectionChanged.append(self.selectionChanged)
        
        self.picload = PicLoader()
        self.picload.addCallback(self.paintPosterPixmap)

        self.tmdb3 = tmdb.init_tmdb3()
        
        self.movie_title = ""
        if self.service is not None:
            self.movie_title = ServiceCenter.getInstance().info(self.service).getName(self.service).encode("utf-8").split(" - ")[0].strip()
            self.progressTimer = eTimer()
            self.progressTimer.callback.append(self.refresh)
            self.progressTimer.start(50, True)
            return

        if service is not None:
            items = [(service,)]
        global fetchingMovies
        if fetchingMovies is None or (fetchingMovies is not None and fetchingMovies.finished):
            fetchingMovies = FetchingMovies(session, items)
        else:
            fetchingMovies.cancel = False
        self.progressTimer = eTimer()
        self.progressTimer.callback.append(self.updateProgress)
        self.progressTimer.start(250, False)
        fetchingMovies.is_hidden = False

    def __onClose(self):
        self.picload.destroy()

    def setWindowTitle(self):
        self.setTitle(_("Search for %s, please wait...") % (self.movie_title))
        self["logo"].instance.setPixmapFromFile(getIconPath("tmdb_logo.png"))

    def scrollLabelPageUp(self):
        self["description"].pageUp()

    def scrollLabelPageDown(self):
        self["description"].pageDown()
    
    def paintPosterPixmap(self, picInfo=None):
        ptr = self.picload.getData()
        if ptr != None:
            self["poster"].instance.setPixmap(ptr)
            self["poster"].show()
    
    def __cancel(self):
        global fetchingMovies
        if fetchingMovies is not None:
            fetchingMovies.cancel = True
        self.close()

    def __hide(self):
        if fetchingMovies is not None:
            fetchingMovies.is_hidden = True
        self.close()
        
    def updateProgress(self):
        self.setTitle(_("Automatic search and save, please wait..."))
        current = 0
        total = 0
        movie_title = ""
        if fetchingMovies is not None:
            current = fetchingMovies.current
            total = fetchingMovies.total
            movie_title = fetchingMovies.movie_title
        self["info"].setText(_("Processing:") + " %d/%d" % (current, total))
        if fetchingMovies is not None and not fetchingMovies.finished:
            self["title"].setText(_("Current Movie: %s") % movie_title)
        else:
            self.setTitle(_("Automatic search and save"))
            self["title"].setText(_("Automatic search and save finished."))
            self["key_green"].setText(_("OK"))
            self.progressTimer.stop()

    def refresh(self):
        self.refreshMovieTitle(self.movie_title)  

    def refreshMovieTitle(self, title):
        self.movie_title = movie_title = title
        self["title"].setText(_("Searchtitle: %s") % movie_title)
        self["info"].setText(_("Filename: %s") % os.path.basename(self.service.getPath()))
        self.setTitle(_("Search result(s) for %s") % (movie_title))
        try:
            results = self.tmdb3.searchMovie(movie_title)
        except:
            results = []
        if len(results) == 0:
            self.setTitle(_("Nothing found for: %s") % (movie_title))
            self["key_green"].setText(_("OK"))
            print "No info found for: " + movie_title
            return False

        self.l = []
        for movie in results:
            try:
                self["key_green"].setText(_("Save infos/cover"))
                released = str(movie.releasedate.year)
                if released:
                    self.l.append((movie.title.encode("utf-8") + " - " + released, movie))
                else:
                    self.l.append((movie.title.encode("utf-8"), movie))
            except:
                pass

        self["list"].setList(self.l)

    def titleSelected(self):
        current = self["list"].l.getCurrentSelection()
        if self.service is not None and current:
            createEIT(self.service.getPath(), self.movie_title, movie=current[1])
        self.__hide()        
    
    def selectionChanged(self):
        self["poster"].hide()
        current = self["list"].l.getCurrentSelection()
        if current:
            try:
                movie = current[1]
                self["description"].setText("%s - %s\n\n%s" % (str(movie.title.encode('utf-8', 'ignore')), str(movie.releasedate), movie.overview.encode('utf-8', 'ignore')))
                jpg_file = "/tmp/preview.jpg"
                cover_url = movie.poster_url
                if cover_url is not None:
                    downloadCover(cover_url, jpg_file, True)
                else:
                    jpg_file = getIconPath("nocover_de.png")
                sc = AVSwitch().getFramebufferScale()
                self.picload.setPara((self["poster"].instance.size().width(), self["poster"].instance.size().height(), sc[0], sc[1], False, 1, "#ff000000"))
                self.picload.startDecode(jpg_file)
            except Exception, e:
                print e
        
    def pageUp(self):
        self["description"].pageUp()

    def pageDown(self):
        self["description"].pageDown()
        
    def editTitle(self):
        self.session.openWithCallback(self.newTitle, VirtualKeyBoard, title=_("Enter new moviename to search for"), text=self.movie_title)
        
    def newTitle(self, newTitle):
        if newTitle is not None:
            self.setTitle(_("Search for %s, please wait...") % (newTitle))
            self.refreshMovieTitle(newTitle.strip())

class FetchingMovies(Thread):
    def __init__(self, session, items):
        Thread.__init__(self, name="AMS-FetchingMoviesThread")
        self.session = session
        self.is_hidden = False
        self.movie_title = ""
        self.current = 0
        self.total = 0
        self.timer = eTimer()
        self.timer.callback.append(self.checkFinished)
        self.items = items
        self.start()
        self.finished = False
        self.timer.start(2000, False)

    def run(self):
        try:
            self.cancel = False
            self.total = len(self.items)
            self.current = 0
            for item_list in self.items:
                try:
                    if self.cancel:
                        #print "Movie download cancelled"
                        return
                    service = item_list[0]
                    if not isinstance(service, eServiceReference):
                        service = service.serviceref
                    if service.flags & eServiceReference.mustDescent:
                        self.total -= 1
                        continue
                    self.current += 1 
                    self.movie_title = ServiceCenter.getInstance().info(service).getName(service).encode("utf-8").split(" - ")[0].strip()
                    createEIT(service.getPath(), self.movie_title)
                except:
                    printStackTrace()
        except:
            printStackTrace()
        finally:
            self.current = self.total
            self.finished = True
    
    def checkFinished(self):
        #print "Movie download finished"
        if self.finished:
            if self.is_hidden == True:
                self.session.open(MessageBox, (_("Download and save from movie infos and covers complete.")), MessageBox.TYPE_INFO, 10, True)
            self.timer.stop()
