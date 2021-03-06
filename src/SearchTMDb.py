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
import shutil
from enigma import RT_WRAP, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, eListboxPythonMultiContent
from GUIListComponent import GUIListComponent
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Components.ActionMap import HelpableActionMap
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from os import path as os_path, mkdir as os_mkdir
from Source.Timer import xTimer
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.AVSwitch import AVSwitch
from Screens.MessageBox import MessageBox
from Components.config import config
from Components.ProgressBar import ProgressBar
from Source.PicLoader import PicLoader
from Source.Globals import pluginPresent, SkinTools, getIconPath, getNocover
from Source.MovieDB import downloadCover
from Source.MovieDB import tmdb
from SkinParam import TMDbSkinParam
import datetime

IMAGE_TEMPFILE = "/tmp/TMDb_temp"

class InfoChecker:
    INFO = 0x01
    COVER = 0x02
    BACKDROP = 0x04
    IMAGES = COVER | BACKDROP
    ALL = INFO | COVER | BACKDROP
    def __init__(self):
        pass
    
    @classmethod
    def check(self, file_name):
        present = 0
        if InfoChecker.checkExtension(file_name, ".eit"):
            present |= InfoChecker.INFO
        if InfoChecker.checkExtension(file_name, ".jpg"):
            present |= InfoChecker.COVER
        if InfoChecker.checkExtension(file_name, ".backdrop.jpg"):
            present |= InfoChecker.BACKDROP
        return present

    @classmethod
    def checkExtension(self, file_name, ext):
        import os
        # DVD directory
        if not os.path.isdir(file_name):
            f_name = os.path.splitext(file_name)[0]
        else:
            f_name = file_name
        file_name = f_name + ext
        return os.path.exists(file_name)

class InfoLoadChoice():
    def __init__(self, callback):
        self.__callback = callback
        self.__timer = xTimer()
        self.__timer.addCallback(self.__timerCallback)
    
    def checkExistence(self, file_name):
        present = InfoChecker.check(file_name)
        default = (False, False, False)
        if False: # TODO: implement settings for disable choice here 
            self.startTimer(default)
            return
        #l.append((_("Only those, which are not available!"), default))
        #if present & InfoChecker.ALL == InfoChecker.ALL:
        #    l.append((_("Overwrite all (description & cover & backdrop)"), (True, True, True)))
        #if present & InfoChecker.INFO:
        #    l.append((_("Overwrite movie description"), (True, False, False)))
        #if present & InfoChecker.COVER:
        #    l.append((_("Overwrite movie cover"), (False, True, False)))
        #if present & InfoChecker.BACKDROP:
        #    l.append((_("Overwrite movie backdrop"), (False, False, True)))

        l = []
        l.append((_("Overwrite movie description"), not bool(present & InfoChecker.INFO)))
        l.append((_("Overwrite movie cover"), True))
        l.append((_("Overwrite movie backdrop"), True))
        if present & InfoChecker.ALL != 0:
            # from Screens.ChoiceBox import ChoiceBox
            # self.session.openWithCallback(self.startTimer, ChoiceBox, title=_("Data already exists! Should anything be updated?"), list=l)
            from SelectionListScreen import SelectionListScreen
            self.session.openWithCallback(self.startTimer, SelectionListScreen, title=_("Data already exists! Should anything be updated?"), list=l)
        else:
            self.__callback(default)

    def startTimer(self, answer):
        print "InfoLoadChoice", answer
        self.answer = answer
        self.__timer.start(100, True)

    def __timerCallback(self):
        self.__callback(self.answer)

class TMDbList(GUIListComponent, TMDbSkinParam, object):
    def __init__(self):
        GUIListComponent.__init__(self)
        TMDbSkinParam.__init__(self)
        self.l.setBuildFunc(self.buildMovieSelectionListEntry)
        self.picloader = PicLoader()
        self.picloader.setSize(self.picSize.width(), self.picSize.height())
        self.build_update_callback = []
        self.list = []

    def destroy(self):
        self.picloader.destroy()
        GUIListComponent.destroy(self)

    def buildMovieSelectionListEntry(self, movie, movie_base=None):
        width = self.l.getItemSize().width()
        height = self.l.getItemSize().height()
        res = [ None ]
        try:
            for callback in self.build_update_callback:
                callback(movie)

            name = movie.Title
            if movie_base:
                name = movie_base + " - " + movie.Title

            if isinstance(movie.ReleaseDate, datetime.date):
                released = str(movie.ReleaseDate.year)
            else:
                released = str(movie.ReleaseDate)

            cover_url = movie.poster_url
            
            if not cover_url:
                png = self.picloader.load(getNocover())
            else:
                parts = cover_url.split("/")
                filename = os_path.join(IMAGE_TEMPFILE, str(movie.ID) + str(parts[-1]))
                print filename
                if downloadCover(cover_url, filename):
                    png = self.picloader.load(filename)
                else:
                    png = self.picloader.load(getNocover())
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, self.picPos.x(), self.picPos.y(), self.picSize.width(), self.picSize.height(), png))
            res.append((eListboxPythonMultiContent.TYPE_TEXT, self.line1Pos.x(), self.line1Pos.y(), width - self.line1Pos.x(), self.f0h, 0, RT_HALIGN_LEFT, name))
            res.append((eListboxPythonMultiContent.TYPE_TEXT, width - 255, self.line1Pos.y(), 250, self.f0h, 0, RT_HALIGN_RIGHT, released))
            res.append((eListboxPythonMultiContent.TYPE_TEXT, self.line2Pos.x(), self.line2Pos.y(), width - self.line2Pos.x(), height - self.line2Pos.y(), 1, RT_WRAP, movie.Overview))
        except:
            from Source.Globals import printStackTrace
            printStackTrace()
        return res
        
    def setList(self, l):
        self.list = l
        self.l.setList(l)
    
    def getCurrent(self):
        return self.l.getCurrentSelection()
    
    def getLength(self):
        return len(self.list)

    
class TMDbMain(Screen, HelpableScreen, InfoLoadChoice):
    SHOW_DETAIL_TEXT = _("Show movie detail")
    SHOW_SEARCH_RESULT_TEXT = _("Show search result")
    MANUAL_SEARCH_TEXT = _("Manual search")
    INFO_SAVE_TEXT = _("Info/Cover save")
    TRAILER_SEARCH_TEXT = _("Trailer search")

    SHOW_SEARCH = 0
    SHOW_SEARCH_NO_RESULT = 1
    SHOW_RESULT_LIST = 2
    SHOW_MOVIE_DETAIL = 3
        
    def __init__(self, session, searchTitle, service=None):
        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        InfoLoadChoice.__init__(self, self.callback_green_pressed)
        self.skinName = ["TMDbMain"]
        if config.AdvancedMovieSelection.show_backdrop.value:
            SkinTools.insertBackdrop(self.skinName)

        self.service = service
        self.movies = []
        if not os_path.exists(IMAGE_TEMPFILE):
            os_mkdir(IMAGE_TEMPFILE)
        self["ColorActions"] = HelpableActionMap(self, "ColorActions",
        {
            "red": (self.red_pressed, _("Toggle detail and list view")),
            "green": (self.green_pressed, _("Save info/cover")),
            "yellow": (self.yellow_pressed, _("Manual search")),
            "blue": (self.blue_pressed, _("Trailer search")),
        }, -1)
        self["WizardActions"] = HelpableActionMap(self, "WizardActions",
        {
            "ok": (self.ok_pressed, _("Toggle detail and list view")),
            "back": (self.cancel, _("Close")),
            "left": (self.left, _("Show previous cover")),
            "right": (self.right, _("Show next cover")),
            "up": (self.moveUp, _("Move up")),
            "down": (self.moveDown, _("Move down")),
        }, -1)
        self["EPGSelectActions"] = HelpableActionMap(self, "EPGSelectActions",
        {
            "nextBouquet": (self.nextBackdrop, _("Show next backdrop")),
            "prevBouquet": (self.prevBackdrop, _("Show previous backdrop")),
        })
        self["ChannelSelectBaseActions"] = HelpableActionMap(self, "ChannelSelectBaseActions",
        {
            "nextMarker": (self.right, _("Show next cover")),
            "prevMarker": (self.left, _("Show previous cover")),
        }, -1)
        self["list"] = TMDbList()
        self["tmdblogo"] = Pixmap()
        self["cover"] = Pixmap()
        self["backdrop"] = Pixmap()
        self.picload = PicLoader()
        self.picload.addCallback(self.paintCoverPixmapCB)
        self.backdrop_picload = PicLoader()
        self.backdrop_picload.addCallback(self.paintBackdropPixmapCB)
        self["description"] = ScrollLabel()
        self["extended"] = Label()
        self["status"] = Label()
        self["stars"] = ProgressBar()
        self["no_stars"] = Pixmap()
        self["vote"] = Label()
        self["result_txt"] = Label()
        self["seperator"] = Pixmap()                
        self["button_red"] = Pixmap()
        self["button_green"] = Pixmap()      
        self["button_yellow"] = Pixmap()
        self["button_blue"] = Pixmap()
        self["key_red"] = StaticText("")
        self["key_green"] = StaticText("")
        self["key_yellow"] = StaticText("")
        self["key_blue"] = StaticText("")
        self.ratingstars = -1
        self.searchTitle = searchTitle
        self.downloadItems = {}
        self.useTMDbInfoAsEventInfo = True
        self.timer = xTimer()
        self.timer.addCallback(self.searchForMovies)
        self.blue_button_timer = xTimer()
        self.blue_button_timer.addCallback(self.callback_blue_pressed) 
        self.onClose.append(self.deleteTempDir)
        self.onLayoutFinish.append(self.layoutFinished)
        self.view_mode = self.SHOW_SEARCH
        self.automatic_show_detail = True

    def layoutFinished(self):
        self["tmdblogo"].instance.setPixmapFromFile(getIconPath("tmdb.png"))
        sc = AVSwitch().getFramebufferScale()
        self.picload.setPara((self["cover"].instance.size().width(), self["cover"].instance.size().height(), sc[0], sc[1], False, 1, "#ff000000"))
        self.backdrop_picload.setPara((self["backdrop"].instance.size().width(), self["backdrop"].instance.size().height(), sc[0], sc[1], False, 1, "#10000000"))
        self.updateView()
        self.startSearch()

    def deleteTempDir(self):
        self.picload.destroy()
        self.backdrop_picload.destroy()
        try:
            shutil.rmtree(IMAGE_TEMPFILE)
        except Exception, e:
            print "[AdvancedMovieSelection] ERROR deleting:", IMAGE_TEMPFILE
            print e

    def startSearch(self):
        self.updateView(self.SHOW_SEARCH)
        self.setTitle(_("TMDb Info & D/L"))
        self["status"].setText(_("Searching for '%s' on TMDb, please wait...") % self.searchTitle)
        self["status"].show()
        self.timer.start(100, True)

    def cancel(self, retval=None):
        self.close(False)

    def getCurrent(self):
        cur = self["list"].getCurrent()
        if cur:
            return cur[0]
    
    def searchForMovies(self):
        try:
            title = self.searchTitle
            results = tmdb.searchMovie(title)
            print "[SerchTMDB]", title, str(len(results))
            if len(results) == 0:
                self.showNoSearchResult()
                return             
            self.movies = []
            for movie in results:
                if movie is not None:
                    self.movies.append((movie,),)
            self["list"].setList(self.movies)
            self.showMovieList()
        except Exception, e:
            from Source.Globals import printStackTrace
            printStackTrace()
            self["status"].setText(_("Error!\n%s" % e))
            self["status"].show()
            return

    def showNoSearchResult(self):
        self.updateView(self.SHOW_SEARCH_NO_RESULT)
        self["status"].setText(_("No data found for '%s' at themoviedb.org!") % self.searchTitle)
        self.session.openWithCallback(self.askForSearchCallback, MessageBox, _("No data found for '%s' at themoviedb.org!\nDo you want to edit the search name?") % self.searchTitle)

    def showMovieList(self):
        count = self["list"].getLength()
        if count == 1 and self.automatic_show_detail:
            txt = _("Total %d movie found") % count
            cur = self["list"].getCurrent()
            if cur is not None:
                self.getMovieInfo(cur[0])
                self.updateView(self.SHOW_MOVIE_DETAIL)
        else:
            self.updateView(self.SHOW_RESULT_LIST)
            txt = _("Total %d movies found") % count
        self["result_txt"].setText(txt) 
        
    def moveUp(self):
        if self.view_mode == self.SHOW_RESULT_LIST:
            self["list"].moveUp()
        else:
            self["description"].pageUp()

    def moveDown(self):
        if self.view_mode == self.SHOW_RESULT_LIST:
            self["list"].moveDown()
        else:
            self["description"].pageDown()

    def askForSearchCallback(self, val):
        if val:
            self.yellow_pressed()
        else:
            self.close()

    def newSearchFinished(self, text=None):
        if text:
            self.searchTitle = text
            self.searchForMovies()

    def getMovieInfo(self, movie):
        try:
            if movie:
                movie.update()

                extended = self.getImageIndexText(movie) + '\n'
                name = movie.Title
                description = movie.Overview
                released = movie.ReleaseDate.year
                certification = movie.Certification
                runtime = movie.Runtime
                if description:
                    self["description"].setText(description)
                else:
                    self["description"].setText(_("No description for '%s' at themoviedb.org found!") % name)
                
                if released:
                    extended += str.format("{0} {1} / ", _("Appeared:"), released)
                if runtime:
                    extended += (_("Runtime: %s minutes") % runtime) + ' / '
                if certification:
                    extended += str.format("{0} {1} / ", _("Certification:"), _(certification))

                extended += str.format("{0} {1:0.1f}", _("Rating:"), movie.UserRating)
                self.ratingstars = int(10 * round(movie.UserRating, 1))
                if self.ratingstars > 0:
                    self["stars"].setValue(self.ratingstars) 
                
                if len(movie.Genres) > 0:
                    extended += str.format("\r\n{0} {1}", _("Genre:"), ", ".join(movie.Genres))
                    
                if len(movie.Writers) > 0:
                    extended += str.format("\r\n{0} {1}", _("From:"), ", ".join(movie.Writers))

                if len(movie.Studios) > 0:
                    extended += str.format("\r\n{0} {1}", _("Studio:"), ", ".join(movie.Studios))

                if len(movie.Directors) > 0:
                    extended += str.format("\r\n{0} {1}", _("Director:"), ", ".join(movie.Directors))
                             
                if len(movie.Producers) > 0:
                    extended += str.format("\r\n{0} {1}", _("Production:"), ", ".join(movie.Producers))

                if len(movie.Cast) > 0:
                    extended += str.format("\r\n{0} {1}", _("Actors:"), ", ".join(movie.Cast))
                
                if movie.Votes != 0:
                    self["vote"].setText(str.format("{0} {1} {2}", _("Voted:"), movie.Votes, _("times")))
                else:
                    self["vote"].setText(_("No user voted!"))

                if extended:
                    self["extended"].setText(extended)
                else:
                    self["extended"].setText(_("Unknown error!!"))
            self.updateView(self.SHOW_MOVIE_DETAIL)
            self.updateCover(movie)
        except Exception, e:
            from Source.Globals import printStackTrace
            printStackTrace()
            self["status"].setText(_("Error!\n%s" % e))
            self["status"].show()
            return

    def paintCoverPixmapCB(self, picInfo=None):
        ptr = self.picload.getData()
        if ptr != None:
            self["cover"].instance.setPixmap(ptr)
            self["cover"].show()

    def paintBackdropPixmapCB(self, picInfo=None):
        ptr = self.backdrop_picload.getData()
        if ptr != None:
            self["backdrop"].instance.setPixmap(ptr)
            self["backdrop"].show()
    
    def imageTMPFileName(self, url, id):
        if url is None:
            return None
        parts = url.split(':')
        parts = parts[1].replace("/", "_")
        return os_path.join(IMAGE_TEMPFILE, str(id) + str(parts))
    
    def updateCover(self, movie):
        if self.view_mode != self.SHOW_MOVIE_DETAIL:
            return
        filename = self.imageTMPFileName(movie.poster_url, movie.ID)
        if downloadCover(movie.poster_url, filename):
            self.picload.startDecode(filename)
        else:
            #self.picload.startDecode(getNocover())
            self["cover"].hide()
        filename = self.imageTMPFileName(movie.backdrop_url, movie.ID)
        if downloadCover(movie.backdrop_url, filename):
            self.backdrop_picload.startDecode(filename)
        else:
            #self.backdrop_picload.startDecode(getNocover())
            self["backdrop"].hide()
    
    def getImageIndexText(self, movie):
        return "%s %d/%d, %s %d/%d" % (_("Cover:"), movie.poster_index, len(movie.poster_urls), _("Backdrop:"), movie.backdrop_index, len(movie.backdrop_urls))
    
    def updateImageIndex(self, method):
        if len(self.movies) == 0:
            return
        index = self["list"].getCurrentIndex()
        cur = self["list"].getCurrent()
        movie = cur[0]
        if len(movie.poster_urls) == 0:
            return
        method(movie)
        self["list"].l.invalidateEntry(index)
        self.getMovieInfo(movie)

    def dummy(self):
        print "Dummy"

    def left(self):
        if self.view_mode == self.SHOW_RESULT_LIST:
            self["list"].pageUp()
        else:
            self.updateImageIndex(tmdb.prevImageIndex)
    
    def right(self):
        if self.view_mode == self.SHOW_RESULT_LIST:
            self["list"].pageDown()
        else:
            self.updateImageIndex(tmdb.nextImageIndex)

    def prevBackdrop(self):
        self.updateImageIndex(tmdb.prevBackdrop)
    
    def nextBackdrop(self):
        self.updateImageIndex(tmdb.nextBackdrop)

    def checkConnection(self):
        try:
            import socket 
            print socket.gethostbyname('www.google.com')
            return True
        except:
            self.session.openWithCallback(self.close, MessageBox, _("No internet connection available!"), MessageBox.TYPE_ERROR)
            return False
    
    def trailerSearch(self, title):
        print str.format("Trailer search: {0}", title)
        if not pluginPresent.YTTrailer:
            print "No plugin found!"
        else:
            from Plugins.Extensions.YTTrailer.plugin import YTTrailerList #@UnresolvedImport
            self.session.open(YTTrailerList, title)
    
    def buttonAction(self, text):
        if text == self.SHOW_DETAIL_TEXT:
            cur = self["list"].getCurrent()
            if cur is not None:
                self.getMovieInfo(cur[0])
        elif text == self.SHOW_SEARCH_RESULT_TEXT:
            self.searchForMovies()
        elif text == self.TRAILER_SEARCH_TEXT:
            self.trailerSearch(self.getCurrent() and self.getCurrent().Title or self.searchTitle)
    
    def red_pressed(self):
        self.ok_pressed()
    
    def ok_pressed(self):
        if self.view_mode == self.SHOW_RESULT_LIST:
            cur = self["list"].getCurrent()
            if cur is not None:
                self.getMovieInfo(cur[0])
                self.updateView(self.SHOW_MOVIE_DETAIL)
        else:
            self.updateView(self.SHOW_RESULT_LIST)

    def green_pressed(self):
        if self.service is None:
            return
        self.setTitle(_("Save Info/Cover for '%s', please wait...") % self.searchTitle)  
        self.checkExistence(self.service.getPath())
        #self.green_button_timer.start(100, True) 

    def callback_green_pressed(self, answer=None):
        if self.checkConnection() == False or not self["list"].getCurrent():
            return
        
        from Source.EITTools import writeEITex, OverwriteSettings
        overwrite = OverwriteSettings()
        overwrite.eit, overwrite.cover, overwrite.backdrop = answer and answer or (False, False, False)
        current_movie = self["list"].getCurrent()[0]
        title = current_movie.Title
        if self.service is not None:
            writeEITex(self.service.getPath(), current_movie, overwrite)
            self.close(False)
        else:
            self.session.openWithCallback(self.close, MessageBox, _("Sorry, no info/cover found for title: %s") % (title), MessageBox.TYPE_ERROR)

    def yellow_pressed(self):
        from AdvancedKeyboard import AdvancedKeyBoard
        self.session.openWithCallback(self.newSearchFinished, AdvancedKeyBoard, title=_("Enter new moviename to search for"), text=self.searchTitle)

    def blue_pressed(self):
        text = self["key_blue"].getText()
        current_movie = self.getCurrent()
        if current_movie:
            title = current_movie.Title
            if text == self.TRAILER_SEARCH_TEXT:
                self.setTitle(_("Search trailer for '%s', please wait...") % title)
            self.blue_button_timer.start(100, True)

    def callback_blue_pressed(self):
        text = self["key_blue"].getText()
        self.buttonAction(text)

    def hideAll(self):
        self["list"].hide()
        self["tmdblogo"].hide()
        self["cover"].hide()
        self["backdrop"].hide()
        self["description"].hide()
        self["extended"].hide()
        self["status"].hide()
        self["stars"].hide()
        self["no_stars"].hide()
        self["vote"].hide()
        self["result_txt"].hide()
        self["seperator"].hide()
        self["button_red"].hide()
        self["button_green"].hide()
        self["button_yellow"].hide()
        self["button_blue"].hide()

    def movieDetailView(self):
        current_movie = self["list"].getCurrent()[0]
        title = current_movie.Title
        self.setTitle(_("Details for: %s") % title)
        self.hideAll()
        self["seperator"].show()
        self["description"].show()
        self["extended"].show()
        if self.ratingstars > 0:
            self["stars"].show()
            self["no_stars"].show()
            self["vote"].show()

    def movieListView(self, title):
        self.setTitle(_("Search result for: %s") % title)
        self.hideAll()
        self["seperator"].show()
        self["tmdblogo"].show()
        self["result_txt"].show()
        self["list"].show()

    def updateView(self, mode=None):
        if mode:
            self.view_mode = mode
        if self.view_mode == self.SHOW_SEARCH:
            self.hideAll()
            self["key_red"].setText("")
            self["key_green"].setText("")
            self["key_yellow"].setText("")
            self["key_blue"].setText("")
            self["tmdblogo"].show()
        elif self.view_mode == self.SHOW_SEARCH_NO_RESULT:
            self.hideAll()
            self["key_red"].setText("")
            self["key_green"].setText("")
            self["key_yellow"].setText(self.MANUAL_SEARCH_TEXT)
            self["key_blue"].setText("")
            self["button_yellow"].show()
            self["tmdblogo"].show()
            self["seperator"].show()
            self["status"].show()
        elif self.view_mode == self.SHOW_RESULT_LIST:
            self.movieListView(self.searchTitle)
            self["key_red"].setText(self.SHOW_DETAIL_TEXT)
            self["key_green"].setText(self.INFO_SAVE_TEXT if self.service is not None else "")
            self["key_yellow"].setText(self.MANUAL_SEARCH_TEXT)
            if pluginPresent.YTTrailer:
                self["key_blue"].setText(self.TRAILER_SEARCH_TEXT)
                self["button_blue"].show()
            else:
                self["key_blue"].setText("")
                self["button_blue"].hide()
            self["button_red"].show()
            if self.service is not None:
                self["button_green"].show()
            self["button_yellow"].show()
        elif self.view_mode == self.SHOW_MOVIE_DETAIL:
            self.movieDetailView()
            self["key_red"].setText(self.SHOW_SEARCH_RESULT_TEXT)
            self["key_green"].setText(self.INFO_SAVE_TEXT if self.service is not None else "")
            self["key_yellow"].setText(self.MANUAL_SEARCH_TEXT)
            if pluginPresent.YTTrailer:
                self["key_blue"].setText(self.TRAILER_SEARCH_TEXT)
                self["button_blue"].show()
            else:
                self["key_blue"].setText("")
                self["button_blue"].hide()
            self["button_red"].show()
            if self.service is not None:
                self["button_green"].show()
            self["button_yellow"].show()
            
