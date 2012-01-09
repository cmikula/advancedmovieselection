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
from enigma import RT_WRAP, RT_VALIGN_CENTER, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, gFont, eListbox, eListboxPythonMultiContent
from Components.GUIComponent import GUIComponent
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from os import path as os_path, mkdir as os_mkdir, rename as os_rename
from Tools.LoadPixmap import LoadPixmap
from enigma import ePicLoad, eTimer
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.AVSwitch import AVSwitch
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.config import config
from shutil import rmtree as shutil_rmtree
from enigma import getDesktop
import tmdb, urllib
from Components.ProgressBar import ProgressBar
import shutil
from os import environ
from ServiceProvider import PicLoader
from Tools.Directories import fileExists

tmdb_logodir = "/usr/lib/enigma2/python/Plugins/Extensions/AdvancedMovieSelection/images"
IMAGE_TEMPFILE = "/tmp/TMDb_temp"

if environ["LANGUAGE"] == "de" or environ["LANGUAGE"] == "de_DE":
    nocover = ("/usr/lib/enigma2/python/Plugins/Extensions/AdvancedMovieSelection/images/nocover_de.png")
else:
    nocover = ("/usr/lib/enigma2/python/Plugins/Extensions/AdvancedMovieSelection/images/nocover_en.png")

if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/YTTrailer/plugin.pyo"):
    from Plugins.Extensions.YTTrailer.plugin import YTTrailerList
    YTTrailerPresent = True
else:
    YTTrailerPresent = False

class TMDbList(GUIComponent, object):
    def __init__(self):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.l.setBuildFunc(self.buildMovieSelectionListEntry)
        self.l.setFont(0, gFont("Regular", 20))
        self.l.setFont(1, gFont("Regular", 17))
        self.l.setItemHeight(140)
        if not os_path.exists(IMAGE_TEMPFILE):
            os_mkdir(IMAGE_TEMPFILE)
        self.picloader = PicLoader(92, 138)

    def buildMovieSelectionListEntry(self, movie, id):
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
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 0, 1, 92, 138, png))
        else:    
            parts = cover_url.split("/")
            filename = os_path.join(IMAGE_TEMPFILE , id + parts[-1])
            urllib.urlretrieve(cover_url, filename)
            png = self.picloader.load(filename)
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 0, 1, 92, 138, png))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, 100, 5, width - 100 , 20, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, "%s" % name.encode('utf-8', 'ignore')))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, width - 140, 5, 130 , 20, 1, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, "%s" % released_text))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, 100, 30, width - 100, 100, 1, RT_WRAP, "%s" % overview))
        return res
        
    def errorThumbDownload(self, error=None):
        if error is not None:
            print "[TMDbList] Error: ", str(error.getErrorMessage())

    def finishedThumbDownload(self, result, temp_filename, filename, index):
        try: 
            os_rename (temp_filename, filename)
        except: pass
        else:
            self.l.invalidateEntry(index)

    GUI_WIDGET = eListbox
    
    def postWidgetCreate(self, instance):
        instance.setContent(self.l)

    def preWidgetRemove(self, instance):
        instance.setContent(None)

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()

    def setList(self, list):
        self.l.setList(list)
    
    def getCurrent(self):
        return self.l.getCurrentSelection()

class TMDbMain(Screen):
    def __init__(self, session, searchTitle, service):
        Screen.__init__(self, session)
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            self.skinName = ["TMDbMainHD"]
        elif sz_w == 1024:
            self.skinName = ["TMDbMainXD"]
        else:
            self.skinName = ["TMDbMainSD"]
        self.service = service
        self["list"] = TMDbList()
        self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions", "EPGSelectActions", "InfobarActions"],
        {
            "ok": self.green_pressed,
            "back": self.cancel,
            "green": self.green_pressed,
            "red": self.red_pressed,
            "blue": self.blue_pressed,
            "yellow": self.yellow_pressed,
            "upUp": self.pageUp,
            "leftUp": self.pageUp,
            "downUp": self.pageDown,
            "rightUp": self.pageDown,
        }, -1)
        self["key_red"] = StaticText("")
        self["key_green"] = StaticText("")
        self["key_yellow"] = StaticText("")
        self["key_blue"] = StaticText("")
        self["tmdblogo"] = Pixmap()
        self["cover"] = Pixmap()
        self["cover"].hide()
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.paintCoverPixmapCB)
        self["description"] = ScrollLabel()
        self["extended"] = Label()
        self["status"] = Label()
        self["stars"] = ProgressBar()
        self["no_stars"] = Pixmap()
        self["stars"].hide()
        self["no_stars"].hide()
        self["vote"] = Label()
        self["button_red"] = Pixmap()
        self["button_red"].hide() 
        self["button_green"] = Pixmap()
        self["button_green"].hide()        
        self["button_yellow"] = Pixmap()
        self["button_yellow"].hide()
        self["button_blue"] = Pixmap()
        self["button_blue"].hide()
        self["result_txt"] = Label()
        self["result_txt"].hide()
        self.resultlist_lock_flag = None
        self.ratingstars = -1
        self.searchTitle = searchTitle
        self.downloadItems = {}
        self.useTMDbInfoAsEventInfo = True
        self.timer = eTimer()
        self.timer.callback.append(self.searchForMovies)
        self.onClose.append(self.deleteTempDir)
        self.onLayoutFinish.append(self.layoutFinished)
        self.startSearch()

    def layoutFinished(self):
        sc = AVSwitch().getFramebufferScale()
        self.picload.setPara((self["cover"].instance.size().width(), self["cover"].instance.size().height(), sc[0], sc[1], False, 1, "#00000000"))

    def deleteTempDir(self):
        try:
            shutil.rmtree(IMAGE_TEMPFILE)
        except Exception, e:
            print "[AdvancedMovieSelection] ERROR deleting:", IMAGE_TEMPFILE
            print e

    def startSearch(self):
        self.setTitle(_("TMDb Info & D/L"))
        self["status"].setText(_("Searching for ' %s ' on TMDb, please wait ...") % self.searchTitle)
        self["status"].show()
        self.timer.start(100, True)

    def cancel(self, retval = None):
        self.close(False)

    def searchForMovies(self):
        self.resultlist_lock_flag = True
        self.setTitle(_("TMDb Info for: %s") % self.searchTitle)
        self["description"].hide()
        self["cover"].hide()
        self["extended"].hide()
        self["list"].hide()
        self["status"].show()
        self["tmdblogo"].instance.setPixmapFromFile("%s/tmdb.png" % tmdb_logodir)
        self["tmdblogo"].show()  
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
                self["status"].setText(_("No data found at themoviedb.org!"))
                self.session.openWithCallback(self.askForSearchCallback, MessageBox, _("No data found at themoviedb.org!\nDo you want to edit the search name?"))
                self["key_yellow"].setText(_("Manual search"))
                self["button_yellow"].show()
                return 
            self["vote"].hide()
            self["stars"].hide()
            self["no_stars"].hide()
            self["result_txt"].setText(_("Search results:"))
            self["result_txt"].show()
            self["key_red"].setText(_("Save movie info/cover"))
            self["key_green"].setText(_("Extended Info"))
            self["key_yellow"].setText(_("Manual search"))
            if YTTrailerPresent:
                self["key_blue"].setText(_("Trailer search"))
                self["button_blue"].show()
            else:
                self["key_blue"].setText("")
                self["button_blue"].hide()                
            self["button_red"].show()
            self["button_green"].show()
            self["button_yellow"].show()
            self["status"].setText("")
            self["status"].hide()
            movies = []
            for searchResult in results:
                id = searchResult['id']
                movies.append((tmdb.getMovieInfo(searchResult['id']), id),)
            self["list"].setList(movies)
            self["list"].show()
        except Exception, e:
            self["status"].setText(_("Error!\n%s" % e))
            return
        
    def pageUp(self):
        self["description"].pageUp()

    def pageDown(self):
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
        self.resultlist_lock_flag = False
        if movie:
            self["result_txt"].hide()
            self["vote"].hide()
            self["status"].hide()
            self["list"].hide()
            self["key_red"].setText(_("Save movie info/cover"))
            self["button_red"].show()
            self["button_green"].show()
            self["key_green"].setText(_("Show search results"))
            self["key_yellow"].setText(_("Manual search"))
            if YTTrailerPresent:
                self["key_blue"].setText(_("Trailer search"))
                self["button_blue"].show()
            else:
                self["key_blue"].setText("")
                self["button_blue"].hide() 
            self["button_yellow"].show()
            self["description"].show()
            self["extended"].show()
            extended = ""
            name = movie["name"].encode('utf-8', 'ignore')
            description = movie["overview"]
            released = movie["released"]
            certification = movie["certification"]
            rating = movie["rating"]
            runtime = movie["runtime"]
            last_modified_at = movie["last_modified_at"]
            self.setTitle(_("TMDb details for: %s") % name)
            if description:
                description_text = description.encode('utf-8', 'ignore')
                self["description"].setText(description_text)
            else:
                self["description"].setText(_("No description for ' %s ' at themoviedb.org found!") % name)
            cover_url = None
            images = movie['images']
            if len(images) > 0:
                cover_url = images[0]['thumb']
            if not cover_url:
                self.setCover(nocover)
            else:    
                parts = cover_url.split("/")
                filename = os_path.join(IMAGE_TEMPFILE , movie['id'] + parts[-1])
                if os_path.exists(filename):
                    self.setCover(filename)
                else:
                    self.setCover(nocover)
            if released:
                extended = (_("Appeared: %s") % released) + ' / '
            if runtime:
                extended += (_("Runtime: %s minutes") % runtime) + ' / '
            if certification:
                if certification == "G":
                    certification = "FSK 0"
                elif certification == "PG":
                    certification = "FSK 6"
                elif certification == "PG-13" or certification == "PG13":
                    certification = "FSK 12"
                elif certification == "R":
                    certification = "FSK 16"
                elif certification == "NC-13" or certification == "NC17":
                    certification = "FSK 18"
                else:
                    certification = "N/A"
                extended += (_("Certification: %s") % certification) + ' / '
            if rating:
                extended += (_("Rating: %s\n") % rating)
                self.ratingstars = int(10*round(float(rating.replace(',','.')),1))
                self["stars"].show()
                self["stars"].setValue(self.ratingstars)
                self["no_stars"].show()                            
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
                vote = movie["votes"].encode('utf-8','ignore')
                if not vote == "0":
                    self["vote"].setText(_("Voted: %s") % (vote) + ' ' + _("times"))
                    self["vote"].show()
                else:
                    self["vote"].hide()
                    self["stars"].hide()
                    self["no_stars"].hide()  

    def errorCoverDownload(self, error=None):
        if error is not None:
            print "[TMDb] Error: ", str(error.getErrorMessage())
        self["cover"].hide()

    def finishedCoverDownload(self, result, filename):
        self["cover"].updatecover(filename)

    def setCover(self, image):
        filename = image
        self.picload.startDecode(filename)

    def paintCoverPixmapCB(self, picInfo=None):
        ptr = self.picload.getData()
        if ptr != None:
            self["cover"].instance.setPixmap(ptr.__deref__())
            self["cover"].show()

    def checkConnection(self):
        try:
            import socket 
            print socket.gethostbyname('www.google.com')
            return True
        except:
            self.session.openWithCallback(self.close, MessageBox, _("No internet connection available!"), MessageBox.TYPE_ERROR)
            return False

    def red_pressed(self):
        if self.checkConnection() == False or not self["list"].getCurrent():
            return
        from EventInformationTable import createEIT
        current_movie = self["list"].getCurrent()[0]
        title = current_movie["name"].encode('utf-8')
        if self.service is not None:
            createEIT(self.service.getPath(), title, config.AdvancedMovieSelection.coversize.value, movie=current_movie)
            self.close(False)
        else:
            self.session.openWithCallback(self.close, MessageBox, _("Sorry, no info/cover found for title: %s") % (title), MessageBox.TYPE_ERROR)

    def green_pressed(self):
        if self.resultlist_lock_flag:
            cur = self["list"].getCurrent()
            if cur is not None:
                self["list"].hide()
                self["status"].setText(_("Getting movie information for '%s' from TMDb...") % cur[1].encode('utf-8', 'ignore'))
                self["status"].show()
                self.getMovieInfo(cur[0])
        else:
            self.searchForMovies()

    def yellow_pressed(self):
        self.session.openWithCallback(self.newSearchFinished, VirtualKeyBoard, title=_("Enter new moviename to search for"), text=self.searchTitle)

    def blue_pressed(self):
        if self.resultlist_lock_flag:
            cur = self["list"].getCurrent()
            if cur is not None:
                cur_tmp = cur[0]
                eventname = cur_tmp['name']
                self.session.open(YTTrailerList, eventname)
        else:
            eventname = self.searchTitle
            self.session.open(YTTrailerList, eventname) 
        