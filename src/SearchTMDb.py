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
import tmdb, urllib, shutil, os
from enigma import RT_WRAP, RT_VALIGN_CENTER, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, gFont, eListbox, eListboxPythonMultiContent
from Components.GUIComponent import GUIComponent
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Components.ActionMap import HelpableActionMap
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from os import path as os_path, mkdir as os_mkdir
from enigma import ePicLoad, eTimer
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.AVSwitch import AVSwitch
from Screens.MessageBox import MessageBox
from Components.config import config
from Components.ProgressBar import ProgressBar
from os import environ
from ServiceProvider import PicLoader
from Tools.Directories import resolveFilename, SCOPE_CURRENT_PLUGIN
from Screens.ChoiceBox import ChoiceBox
from Globals import pluginPresent, SkinTools

IMAGE_TEMPFILE = "/tmp/TMDb_temp"

if environ["LANGUAGE"] == "de" or environ["LANGUAGE"] == "de_DE":
    nocover = resolveFilename(SCOPE_CURRENT_PLUGIN, "Extensions/AdvancedMovieSelection/images/nocover_de.png")
else:
    nocover = resolveFilename(SCOPE_CURRENT_PLUGIN, "Extensions/AdvancedMovieSelection/images/nocover_en.png")

class InfoChecker:
    INFO = 0x01
    COVER = 0x02
    BOTH = INFO | COVER
    def __init__(self):
        pass
    
    @classmethod
    def check(self, file_name):
        present = 0
        if InfoChecker.checkExtension(file_name, ".eit"):
            present |= InfoChecker.INFO
        if InfoChecker.checkExtension(file_name, ".jpg"):
            present |= InfoChecker.COVER
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
        self.__timer = eTimer()
        self.__timer.callback.append(self.__timerCallback)
    
    def checkExistEnce(self, file_name):
        list = []
        present = InfoChecker.check(file_name)
        default = (False, False)
        if False: # TODO: implement settings for disable choice here 
            self.startTimer(default)
            return
        list.append((_("Only those, which are not available!"), default))
        if present & InfoChecker.BOTH == InfoChecker.BOTH:
            list.append((_("Overwrite both (description & cover)"), (True, True)))
        if present & InfoChecker.INFO:
            list.append((_("Overwrite movie description"), (True, False)))
        if present & InfoChecker.COVER:
            list.append((_("Overwrite movie cover"), (False, True)))
            
        if present & InfoChecker.BOTH != 0:
            self.session.openWithCallback(self.startTimer, ChoiceBox, title=_("Data already exists! Should anything be updated?"), list=list)
        else:
            self.__callback(("Default", default))

    def startTimer(self, answer):
        print "InfoLoadChoice", answer
        self.answer = answer
        self.__timer.start(100, True)

    def __timerCallback(self):
        self.__callback(self.answer)

class TMDbList(GUIComponent, object):
    def __init__(self):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.l.setBuildFunc(self.buildMovieSelectionListEntry)
        self.l.setFont(0, gFont("Regular", 20))
        self.l.setFont(1, gFont("Regular", 17))
        self.l.setItemHeight(140)
        self.picloader = PicLoader(92, 138)

    def destroy(self):
        self.picloader.destroy()
        GUIComponent.destroy(self)

    def buildMovieSelectionListEntry(self, movie, movie_id):
        width = self.l.getItemSize().width()
        res = [ None ]
        name = movie['name']
        overview = movie['overview']
        released = movie['released']
        images = movie['images']        
        if overview:
            overview = overview.encode('utf-8', 'ignore')
        else:
            overview = ""
        if released:
            released_text = released
        else:
            released_text = ""
        cover_url = None
        if len(images) > 0:
            cover_url = images[0]['thumb']
        if not cover_url:
            png = self.picloader.load(nocover)
        else:
            parts = cover_url.split("/")
            filename = os_path.join(IMAGE_TEMPFILE , movie_id + parts[-1])
            if not os.path.exists(filename):
                urllib.urlretrieve(cover_url, filename)
            png = self.picloader.load(filename)        
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 0, 1, 92, 138, png))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, 100, 5, width - 100 , 20, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, "%s" % name.encode('utf-8', 'ignore')))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, width - 140, 5, 130 , 20, 1, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, "%s" % released_text))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, 100, 30, width - 100, 100, 1, RT_WRAP, "%s" % overview))
        return res
        
    GUI_WIDGET = eListbox
    
    def postWidgetCreate(self, instance):
        instance.setContent(self.l)

    def preWidgetRemove(self, instance):
        instance.setContent(None)

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()

    def setList(self, list):
        self.list = list
        self.l.setList(list)
    
    def getCurrent(self):
        return self.l.getCurrentSelection()
    
    def getLength(self):
        return len(self.list)

    def moveUp(self):
        self.instance.moveSelection(self.instance.moveUp)

    def moveDown(self):
        self.instance.moveSelection(self.instance.moveDown)

    
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
        
    def __init__(self, session, searchTitle, service):
        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        InfoLoadChoice.__init__(self, self.callback_green_pressed)
        self.skinName = SkinTools.appendResolution("TMDbMain")
        self.service = service
        self.movies = []
        if not os_path.exists(IMAGE_TEMPFILE):
            os_mkdir(IMAGE_TEMPFILE)
        self["ColorActions"] = HelpableActionMap(self, "ColorActions",
        {
            "red": (self.ok_pressed, _("Toggle detail and list view")),
            "green": (self.green_pressed, _("Save info and cover")),
            "yellow": (self.yellow_pressed, _("Manual search")),
            "blue": (self.blue_pressed, _("Trailer search")),
        }, -1)
        self["WizardActions"] = HelpableActionMap(self, "WizardActions",
        {
            "ok": (self.ok_pressed, _("Toggle detail and list view")),
            "back": (self.cancel, _("Exit")),
            "left": (self.left, _("Show previous cover")),
            "right": (self.right, _("Show next cover")),
            "up": (self.moveUp, _("Select preview item in list")),
            "down": (self.moveDown, _("Select next item in list")),
        }, -1)
        self["list"] = TMDbList()
        self["tmdblogo"] = Pixmap()
        self["cover"] = Pixmap()
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.paintCoverPixmapCB)
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
        self.timer = eTimer()
        self.timer.callback.append(self.searchForMovies)
        self.blue_button_timer = eTimer()
        self.blue_button_timer.callback.append(self.callback_blue_pressed) 
        self.onClose.append(self.deleteTempDir)
        self.onLayoutFinish.append(self.layoutFinished)
        self.view_mode = self.SHOW_SEARCH
        self.updateView()
        self.startSearch()

    def layoutFinished(self):
        self["tmdblogo"].instance.setPixmapFromFile(resolveFilename(SCOPE_CURRENT_PLUGIN, "Extensions/AdvancedMovieSelection/images/tmdb.png"))
        sc = AVSwitch().getFramebufferScale()
        self.picload.setPara((self["cover"].instance.size().width(), self["cover"].instance.size().height(), sc[0], sc[1], False, 1, "#00000000"))

    def deleteTempDir(self):
        try:
            shutil.rmtree(IMAGE_TEMPFILE)
        except Exception, e:
            print "[AdvancedMovieSelection] ERROR deleting:", IMAGE_TEMPFILE
            print e

    def startSearch(self):
        self.updateView(self.SHOW_SEARCH)
        self.setTitle(_("TMDb Info & D/L"))
        self["status"].setText(_("Searching for ' %s ' on TMDb, please wait ...") % self.searchTitle)
        self["status"].show()
        self.timer.start(100, True)

    def cancel(self, retval=None):
        self.close(False)

    def searchForMovies(self):
        try:
            results = tmdb.search(self.searchTitle)
            if len(results) == 0 and " - " in self.searchTitle:
                title = self.searchTitle.split(" - ")[0].strip()
                results = tmdb.search(title)
                if len(results) > 0:
                    self.searchTitle = title
            if len(results) == 0 and " & " in self.searchTitle:
                title = self.searchTitle.split(" & ")[0].strip()
                results = tmdb.search(title)
                if len(results) > 0:
                    self.searchTitle = title
            if len(results) == 0 and self.searchTitle.endswith(".ts"):
                title = self.searchTitle[:-3]
                results = tmdb.search(title)
                if len(results) > 0:
                    self.searchTitle = title
            if len(results) == 0:
                self.updateView(self.SHOW_SEARCH_NO_RESULT)
                self["status"].setText(_("No data found for ' %s ' at themoviedb.org!") % self.searchTitle)
                self.session.openWithCallback(self.askForSearchCallback, MessageBox, _("No data found for ' %s ' at themoviedb.org!\nDo you want to edit the search name?") % self.searchTitle)
                return             
            self.movies = []
            for searchResult in results:
                movie_id = searchResult['id']
                self.movies.append((tmdb.getMovieInfo(searchResult['id']), movie_id),)
            self["list"].setList(self.movies)
            self.showMovieList()
        except Exception, e:
            self["status"].setText(_("Error!\n%s" % e))
            self["status"].show()
            return

    def showMovieList(self):
        count = self["list"].getLength()
        if count == 1:
            txt = (_("Total %s") % count + ' ' + _("movie found"))
            cur = self["list"].getCurrent()
            if cur is not None:
                self.getMovieInfo(cur[0])
                self.updateView(self.SHOW_MOVIE_DETAIL)
        else:
            self.updateView(self.SHOW_RESULT_LIST)
            txt = (_("Total %s") % count + ' ' + _("movies found"))
        self["result_txt"].setText(txt) 
        
    def pageUp(self):
        self["description"].pageUp()

    def pageDown(self):
        self["description"].pageDown()

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
                extended = ""
                name = movie["name"].encode('utf-8', 'ignore')
                description = movie["overview"]
                released = movie["released"]
                rating = movie["rating"]
                runtime = movie["runtime"]
                last_modified_at = movie["last_modified_at"]
                if description:
                    description_text = description.encode('utf-8', 'ignore')
                    self["description"].setText(description_text)
                else:
                    self["description"].setText(_("No description for ' %s ' at themoviedb.org found!") % name)
                
                if released:
                    extended = (_("Appeared: %s") % released) + ' / '
                if runtime:
                    extended += (_("Runtime: %s minutes") % runtime) + ' / '

                certification = tmdb.decodeCertification(movie["certification"])
                if certification:
                    extended += (_("Certification: %s") % _(certification)) + ' / '

                if movie.has_key("rating"):
                    rating = movie["rating"].encode('utf-8', 'ignore')    
                    extended += (_("Rating: %s\n") % rating)
                    self.ratingstars = int(10 * round(float(rating.replace(',', '.')), 1))
                    if self.ratingstars > 0:
                        self["stars"].setValue(self.ratingstars) 
                        #self["stars"].show()
                        #self["no_stars"].show()
                if movie.has_key('categories') and movie['categories'].has_key('genre'):                      
                    categories = []
                    for genre in movie['categories']['genre']:
                        categories.append(genre.encode('utf-8', 'ignore'))
                    if len(categories) > 0:
                        extended += _("Genre: %s\n") % ", ".join(categories)             
                if movie.has_key('studios'):
                    studios = []
                    for studio in movie["studios"]:
                        studios.append(studio.encode('utf-8', 'ignore'))
                    if len(studios) > 0:
                        extended += _("Studio: %s") % ", ".join(studios) + ' / '
                if movie.has_key('countries'):
                    countries = []
                    for country in movie["countries"]:
                        countries.append(country.encode('utf-8', 'ignore'))
                    if len(countries) > 0:
                        extended += _("Production Countries: %s\n") % ", ".join(countries)
                if movie.has_key('cast') and movie['cast'].has_key('director'):                      
                    director = []
                    for dir in movie['cast']['director']:
                        director.append(dir['name'].encode('utf-8', 'ignore'))
                    if len(director) > 0:
                        extended += _("Director: %s") % ", ".join(director) + ' / '
                if movie.has_key('cast') and movie['cast'].has_key('producer'):                      
                    producer = []
                    for prodr in movie['cast']['producer']:
                        producer.append(prodr['name'].encode('utf-8', 'ignore'))
                    if len(producer) > 0:
                        extended += _("Production: %s\n") % ", ".join(producer)
                if movie.has_key('cast') and movie['cast'].has_key('actor'):                      
                    actors = []
                    for actor in movie['cast']['actor']:
                        actors.append(actor['name'].encode('utf-8', 'ignore'))
                    if len(actors) > 0:
                        extended += _("Actors: %s\n") % ", ".join(actors)
                if last_modified_at:
                    extended += (_("\nLast modified at themoviedb.org: %s") % last_modified_at)
                if extended:
                    self["extended"].setText(extended)
                else:
                    self["extended"].setText(_("Unknown error!!"))
                if movie.has_key("votes"):
                    vote = movie["votes"].encode('utf-8', 'ignore')
                    if not vote == "0":
                        self["vote"].setText(_("Voted: %s") % (vote) + ' ' + _("times"))
                    else:
                        self["vote"].setText(_("No user voted!"))
            self.updateView(self.SHOW_MOVIE_DETAIL)
            self.updateCover(movie)
        except Exception, e:
            self["status"].setText(_("Error!\n%s" % e))
            self["status"].show()
            return

    def paintCoverPixmapCB(self, picInfo=None):
        ptr = self.picload.getData()
        if ptr != None:
            self["cover"].instance.setPixmap(ptr.__deref__())
            self["cover"].show()

    def updateCover(self, movie):
        if self.view_mode != self.SHOW_MOVIE_DETAIL:
            return
        images = movie['images']
        cover_url = None
        if len(images) > 0:
            cover_url = images[0]['thumb']
        if not cover_url:
            self.picload.startDecode(nocover)
        else:    
            parts = cover_url.split("/")
            filename = os_path.join(IMAGE_TEMPFILE , movie['id'] + parts[-1])
            if not os.path.exists(filename):
                urllib.urlretrieve(cover_url, filename)
            if os_path.exists(filename):
                self.picload.startDecode(filename)
            else:
                self.picload.startDecode(nocover)

    def updateImageIndex(self, method):
        if len(self.movies) == 0:
            return
        index = self["list"].getCurrentIndex()
        cur = self["list"].getCurrent()
        movie = cur[0]
        if len(movie['images']) == 0:
            return
        method(movie)
        cnt = 0
        while not movie['images'][0].has_key(config.AdvancedMovieSelection.coversize.value) and cnt < len(movie['images']):
            method(movie)
            cnt += 1
        self.movies[index] = (movie, cur[1])
        self["list"].l.invalidateEntry(index)
        self.updateCover(movie)

    def dummy(self):
        print "Dummy"

    def left(self):
        self.updateImageIndex(tmdb.prevImageIndex)
    
    def right(self):
        self.updateImageIndex(tmdb.nextImageIndex)

    def checkConnection(self):
        try:
            import socket 
            print socket.gethostbyname('www.google.com')
            return True
        except:
            self.session.openWithCallback(self.close, MessageBox, _("No internet connection available!"), MessageBox.TYPE_ERROR)
            return False

    def buttonAction(self, text):
        if text == self.SHOW_DETAIL_TEXT:
            cur = self["list"].getCurrent()
            if cur is not None:
                self.getMovieInfo(cur[0])
        elif text == self.SHOW_SEARCH_RESULT_TEXT:
            self.searchForMovies()
        elif text == self.TRAILER_SEARCH_TEXT:
            if pluginPresent.YTTrailer:
                current_movie = self["list"].getCurrent()[0]
                title = current_movie["name"].encode('utf-8')
                if self.view_mode == self.SHOW_RESULT_LIST:
                    self.setTitle(_("Search result for: %s") % self.searchTitle)
                else:
                    self.setTitle(_("Details for: %s") % title)
                from Plugins.Extensions.YTTrailer.plugin import YTTrailerList
                self.session.open(YTTrailerList, title)

    def ok_pressed(self):
        if self.view_mode == self.SHOW_RESULT_LIST:
            cur = self["list"].getCurrent()
            if cur is not None:
                self.getMovieInfo(cur[0])
                self.updateView(self.SHOW_MOVIE_DETAIL)
        else:
            self.updateView(self.SHOW_RESULT_LIST)

    def green_pressed(self):
        self.setTitle(_("Save Info/Cover for ' %s ', please wait ...") % self.searchTitle)  
        self.checkExistEnce(self.service.getPath())
        #self.green_button_timer.start(100, True) 

    def callback_green_pressed(self, answer=None):
        if self.checkConnection() == False or not self["list"].getCurrent():
            return
        overwrite_eit, overwrite_jpg = answer and answer[1] or (False, False)
        from EventInformationTable import createEIT
        current_movie = self["list"].getCurrent()[0]
        title = current_movie["name"].encode('utf-8')
        if self.service is not None:
            createEIT(self.service.getPath(), title, config.AdvancedMovieSelection.coversize.value, movie=current_movie, overwrite_jpg=overwrite_jpg, overwrite_eit=overwrite_eit)
            self.close(False)
        else:
            self.session.openWithCallback(self.close, MessageBox, _("Sorry, no info/cover found for title: %s") % (title), MessageBox.TYPE_ERROR)

    def yellow_pressed(self):
        from AdvancedKeyboard import AdvancedKeyBoard
        self.session.openWithCallback(self.newSearchFinished, AdvancedKeyBoard, title=_("Enter new moviename to search for"), text=self.searchTitle)

    def blue_pressed(self):
        text = self["key_blue"].getText()
        current_movie = self["list"].getCurrent()[0]
        title = current_movie["name"].encode('utf-8')
        if text == self.TRAILER_SEARCH_TEXT:
            self.setTitle(_("Search trailer for ' %s ', please wait ...") % title)
        self.blue_button_timer.start(100, True)

    def callback_blue_pressed(self):
        text = self["key_blue"].getText()
        self.buttonAction(text)

    def hideAll(self):
        self["list"].hide()
        self["tmdblogo"].hide()
        self["cover"].hide()
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
        title = current_movie["name"].encode('utf-8')
        self.setTitle(_("Details for: %s") % title)
        self.hideAll()
        self["seperator"].show()
        self["description"].show()
        self["extended"].show()
        if self.ratingstars > 0:
            self["stars"].show()
            self["no_stars"].show()
            self["vote"].show()

    def movieListView(self):
        self.setTitle(_("Search result for: %s") % self.searchTitle)
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
            self.movieListView()
            self["key_red"].setText(self.SHOW_DETAIL_TEXT)
            self["key_green"].setText(self.INFO_SAVE_TEXT)
            self["key_yellow"].setText(self.MANUAL_SEARCH_TEXT)
            if pluginPresent.YTTrailer:
                self["key_blue"].setText(self.TRAILER_SEARCH_TEXT)
                self["button_blue"].show()
            else:
                self["key_blue"].setText("")
                self["button_blue"].hide()
            self["button_red"].show()
            self["button_green"].show()
            self["button_yellow"].show()
        elif self.view_mode == self.SHOW_MOVIE_DETAIL:
            self.movieDetailView()
            self["key_red"].setText(self.SHOW_SEARCH_RESULT_TEXT)
            self["key_green"].setText(self.INFO_SAVE_TEXT)
            self["key_yellow"].setText(self.MANUAL_SEARCH_TEXT)
            if pluginPresent.YTTrailer:
                self["key_blue"].setText(self.TRAILER_SEARCH_TEXT)
                self["button_blue"].show()
            else:
                self["key_blue"].setText("")
                self["button_blue"].hide()
            self["button_red"].show()
            self["button_green"].show()
            self["button_yellow"].show()
            
