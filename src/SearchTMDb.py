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
import xml.etree.cElementTree
from twisted.web.client import downloadPage, getPage
from enigma import RT_WRAP, RT_VALIGN_CENTER, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, gFont, eListbox, eListboxPythonMultiContent
from Components.GUIComponent import GUIComponent
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from urllib import quote as urllib_quote
from os import path as os_path, mkdir as os_mkdir, rename as os_rename
from Tools.LoadPixmap import LoadPixmap
from enigma import ePicLoad
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.AVSwitch import AVSwitch
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.config import config
from shutil import rmtree as shutil_rmtree
from enigma import getDesktop
from collections import defaultdict

tmdb_logodir = "/usr/lib/enigma2/python/Plugins/Extensions/AdvancedMovieSelection/images"
IMAGE_TEMPFILE = "/tmp/cover_temp"
HTTP_THEMOVIEDB = "http://www.themoviedb.org"
API_THEMOVIEDB = "http://api.themoviedb.org/"
API_THEMOVIEDB_VERSION = "2.1/"
API_THEMOVIEDB_SEARCH = "Movie.search/"
API_THEMOVIEDB_MOVIEINFO = "Movie.getInfo/"
#API_THEMOVIEDB_DEVELOPERKEY = "5280daef249da5c45994c9b523ec7e7a/" #key von dr.best
API_THEMOVIEDB_DEVELOPERKEY = "1f834eb425728133b9a2c1c0c82980eb/"
movie_title = ""

def download(url, filename):
    return downloadPage(url, file(filename, 'wb'))

class Movie(dict):
    def __repr__(self):
        return "<Movie: %s (%s)>" % (self.get("name"), self.get("original_name"))

class ddict(defaultdict):
    def __init__(self):
        self.default_factory = type(self)

class Images(ddict):
    def setData(self, element):
        for el in element:
            image = el.get("url")
            if image:
                if image.startswith("http://"): # API change 2010-11-16 ?
                    self[el.get("size")][el.get("width")][el.get("id")] = image
                else:
                    self[el.get("size")][el.get("width")][el.get("id")] = HTTP_THEMOVIEDB + image
        
class Categories(dict):
    def setData(self, element):
        for el in element:
            if el.get("type") and el.get("type") == "genre" and el.get("id"):
                self[el.get("id")] = el.get("name")


class Studios(dict):
    def setData(self, element):
        for el in element:
            if el.get("id") and el.get("name"):
                self[el.get("id")] = el.get("name")

class Countries(dict):
    def setData(self, element):
        for el in element:
            if el.get("code") and el.get("name"):
                self[el.get("code")] = el.get("name")

class Cast(dict):
    def setData(self, element):
        for el in element:
            if el.get("cast_id"):
                self[el.get("cast_id")] = Person(el.get("job"), el.get("name"), el.get("character"), el.get("thumb"), el.get("order"))

class Person(dict):
    def __init__(self, job, name, character, thumb, order):
        self['job'] = job
        self['name'] = name
        self['character'] = character
        if thumb:
            if thumb.startswith("http://"): # API change 2010-11-16 ?
                self['thumb'] = thumb
            else:
                self['thumb'] = HTTP_THEMOVIEDB + thumb
        else:
            self['thumb'] = ""
        self['order'] = order

class TMDb(object):
    def __init__(self):
        self.language = config.osd.language.value.split("_")[0]

    def searchForMovies(self, title, callback):
        self.callback = callback
        url = API_THEMOVIEDB + API_THEMOVIEDB_VERSION + API_THEMOVIEDB_SEARCH + self.language + "/xml/" + API_THEMOVIEDB_DEVELOPERKEY + urllib_quote(title)
        getPage(url, timeout=10).addCallback(self.callbackRequest).addErrback(self.callbackRequestError)        

    def getMovieInfo(self, movie_id, callback):
        self.callback = callback
        url = API_THEMOVIEDB + API_THEMOVIEDB_VERSION + API_THEMOVIEDB_MOVIEINFO + self.language + "/xml/" + API_THEMOVIEDB_DEVELOPERKEY + movie_id
        getPage(url, timeout=10).addCallback(self.callbackRequest).addErrback(self.callbackRequestError)    

    def callbackRequest(self, xmlstring):
        cur_movie_list = []
        root = xml.etree.cElementTree.fromstring(xmlstring)
        if root:
            for childs in root.findall("movies"):
                for childs2 in childs.findall("movie"):
                    cur_movie = {}
                    cur_images = Images()
                    cur_categories = Categories()
                    cur_studios = Studios()
                    cur_countries = Countries()
                    cur_cast = Cast()
                    for  elt in childs2.getiterator():
                        if elt.tag.lower() == "images":
                            cur_images.setData(elt.getiterator())
                        elif elt.tag.lower() == "categories":
                            cur_categories.setData(elt.getiterator())
                        elif elt.tag.lower() == "studios":
                            cur_studios.setData(elt.getiterator())
                        elif elt.tag.lower() == "countries":
                            cur_countries.setData(elt.getiterator())
                        elif elt.tag.lower() == "cast":
                            cur_cast.setData(elt.getiterator())
                        else:
                            if elt.tag and elt.text:
                                cur_movie[elt.tag] = elt.text
                    cur_movie['images'] = cur_images
                    cur_movie['categories'] = cur_categories
                    cur_movie['studios'] = cur_studios
                    cur_movie['countries'] = cur_countries
                    cur_movie['cast'] = cur_cast
                    cur_movie_list.append((cur_movie),)
        self.callback(cur_movie_list, None)

    def callbackRequestError(self, error=None):
        if error is not None:
            self.callback([], str(error.getErrorMessage()))

class TMDbList(GUIComponent, object):
    def buildMovieSelectionListEntry(self, movie_id, name, description, released, cover, thumb):
        width = self.l.getItemSize().width()
        res = [ None ]
        if description:
            description = description.encode('utf-8', 'ignore')
        else:
            description = ""
        if released:
            released_text = released
        else:
            released_text = ""
        if thumb:
            parts = thumb.split("/")
            filename = os_path.join(IMAGE_TEMPFILE , movie_id + parts[-1])
            if not os_path.exists(filename):
                index = self.getCurrentIndex()
                temp_filename = filename + ".tmp"
                download(thumb, temp_filename).addErrback(self.errorThumbDownload).addCallback(self.finishedThumbDownload, temp_filename, filename, index)
            else:
                png = LoadPixmap(cached=True, path=filename)
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 0, 1, 92, 138, png))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, 100, 5, width - 100 , 20, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, "%s" % name.encode('utf-8', 'ignore')))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, width - 140, 5, 130 , 20, 1, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, "%s" % released_text))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, 100, 30, width - 100, 100, 1, RT_WRAP, "%s" % description))
        return res
        
    def __init__(self):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.l.setBuildFunc(self.buildMovieSelectionListEntry)
        self.l.setFont(0, gFont("Regular", 20))
        self.l.setFont(1, gFont("Regular", 17))
        self.l.setItemHeight(140)
        if not os_path.exists(IMAGE_TEMPFILE):
            os_mkdir(IMAGE_TEMPFILE)

    def errorThumbDownload(self, error=None):
        if error is not None:
            print "[TMDbList] Error: ", str(error.getErrorMessage())

    def finishedThumbDownload(self, result, temp_filename, filename, index):
        try: # if you scroll too fast, a thumb-download is started twice...
            os_rename (temp_filename, filename)
        except: pass # i do not care for errors...
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

class Moviecover(Pixmap):
    def __init__(self, callback=None):
        Pixmap.__init__(self)
        self.coverFileName = ""
        if callback:
            self.callback = callback
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.paintIconPixmapCB)

    def onShow(self):
        Pixmap.onShow(self)
        sc = AVSwitch().getFramebufferScale()
        self.picload.setPara((self.instance.size().width(), self.instance.size().height(), sc[0], sc[1], False, 1, "#00000000"))

    def paintIconPixmapCB(self, picInfo=None):
        ptr = self.picload.getData()
        if ptr != None:
            self.instance.setPixmap(ptr.__deref__())
            if self.callback:
                self.callback()

    def updatecover(self, filename):
        new_coverFileName = filename
        if (self.coverFileName != new_coverFileName):
            self.coverFileName = new_coverFileName
            self.picload.startDecode(self.coverFileName)
        else:
            if self.callback:
                self.callback()

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
            "ok": self.blue_pressed,
            "back": self.red_pressed,
            "green": self.green_pressed,
            "red": self.red_pressed,
            "blue": self.blue_pressed,
            "yellow": self.yellow_pressed,
            "upUp": self.pageUp,
            "leftUp": self.pageUp,
            "downUp": self.pageDown,
            "rightUp": self.pageDown,
        }, -1)
        self["key_red"] = StaticText(_("Close"))
        self["key_green"] = StaticText("")
        self["key_yellow"] = StaticText(_("Manual search"))
        self["key_blue"] = StaticText(_("Extended Info"))
        self["tmdblogo"] = Pixmap()
        self["cover"] = Moviecover(self.moviecoverPainted)
        self["cover"].hide()
        self["description"] = ScrollLabel()
        self["extended"] = Label()
        self["status"] = Label()
        self.searchTitle = searchTitle
        self.downloadItems = {}
        self.useTMDbInfoAsEventInfo = True
        self.onLayoutFinish.append(self.searchForMovies)

    def searchForMovies(self):
        self["status"].setText(_("Searching for '%s' from TMDb...") % self.searchTitle)
        self.setTitle(_("TMDb search for: %s") % self.searchTitle)
        self["description"].hide()
        self["cover"].hide()
        self["extended"].hide()
        self["list"].hide()
        self["status"].show()
        self["tmdblogo"].instance.setPixmapFromFile("%s/tmdb.png" % tmdb_logodir)
        self["tmdblogo"].show()
        tmdb = TMDb()
        tmdb.searchForMovies(self.searchTitle, self.searchForMoviesCallback)

    def searchForMoviesCallback(self, movielist, errorString):
        if not errorString:
            if movielist:
                tmpList = []
                for movie in movielist:
                    if movie.has_key("id") and movie.has_key("name"):
                        movie_id = movie["id"]
                        name = movie["name"]
                        if movie.has_key("overview"):
                            description = movie["overview"]
                        else:
                            description = ""
                        if movie.has_key("released"):
                            released = movie["released"]
                        else:
                            released = ""
                        cover = ""
                        thumb = ""
                        for id in movie["images"]["cover"]["185"]:
                            cover = movie["images"]["cover"]['185'][id]
                            break
                        for id in movie["images"]["thumb"]["92"]:
                            thumb = movie["images"]['thumb']['92'][id]
                            break
                        tmpList.append((movie_id, name, description, released, cover, thumb),)
                if not errorString:
                    self["key_green"].text = _("Save movie info/cover")
                else:
                    self["key_green"].text = _()
                self["key_blue"].text = _("Extended Info")
                self["status"].setText("")
                self["status"].hide()
                self["list"].setList(tmpList)
                self["list"].show()
            else:
                self["status"].setText(_("No data found at themoviedb.org!"))
                self["key_green"].text = ""
                self["key_blue"].text = ""
                self.session.openWithCallback(self.askForSearchCallback, MessageBox, _("No data found at themoviedb.org!\nDo you want to edit the search name?"))

        else:
            self["status"].setText(_("Error!\n%s" % errorString))
            self["key_green"].text = ""
            self["key_blue"].text = ""

    def pageUp(self):
        self["description"].pageUp()

    def pageDown(self):
        self["description"].pageDown()

    def askForSearchCallback(self, val):
        if val:
            self.yellow_pressed()
        else:
            self.red_pressed()

    def yellow_pressed(self):
        self.session.openWithCallback(self.newSearchFinished, VirtualKeyBoard, title=_("Enter new moviename to search for"), text=self.searchTitle)

    def newSearchFinished(self, text=None):
        if text:
            self.searchTitle = text
            self.searchForMovies()

    def red_pressed(self):
        if os_path.exists(IMAGE_TEMPFILE):
            shutil_rmtree(IMAGE_TEMPFILE)
        self.close(None)

    def blue_pressed(self):
        cur = self["list"].getCurrent()
        if cur is not None:
                self["list"].hide()
                self["status"].setText(_("Getting movie information for '%s' from TMDb...") % cur[1].encode('utf-8', 'ignore'))
                self["status"].show()
                tmdb = TMDb()
                tmdb.getMovieInfo(cur[0], self.getMovieInfoCallback)

    def getMovieInfoCallback(self, movielist, errorString):
        if not errorString:
            if movielist:
                self["status"].hide()
                self["list"].hide()
                self["key_blue"].text = _("Extended Info")
                self["key_green"].text = _("Save movie info/cover")
                self["key_yellow"].text = _("Manual search")
                self["description"].show()
                self["extended"].show()
                for movie in movielist:
                    extended = ""
                    #movie_id = movie["id"]
                    name = movie["name"].encode('utf-8', 'ignore')
                    description = movie["overview"]
                    released = movie["released"]
                    self.setTitle(_("TMDb movie info for: %s") % name)
                    if description:
                        description_text = description.encode('utf-8', 'ignore')
                        self["description"].setText(name + "\n\n" + description_text)
                    else:
                        self["description"].setText(name)
                    cur = self["list"].getCurrent()
                    cover = cur[4]
                    if cover:
                        #parts = cover.split("/")
                        filename = os_path.join(IMAGE_TEMPFILE , name + '.jpg')
                        if not os_path.exists(filename):
                            download(cover, filename).addErrback(self.errorCoverDownload).addCallback(self.finishedCoverDownload, filename)
                        else:
                            self["cover"].updatecover(filename)
                    if released:
                        extended = (_("Appeared: %s\n") % released)
                    categories = ""
                    for id in movie["categories"]:
                        categories += movie["categories"][id] + ", "
                    if categories:
                        extended += _("Genre: %s\n") % categories[:-2] 
                    studios = ""
                    for id in movie["studios"]:
                        studios += movie["studios"][id] + ", "
                    if studios:
                        extended += _("Studio: %s\n") % studios[:-2]
                    else:
                        extended += "\n"
                    director = ""                    
                    for id in movie["cast"]:
                        if movie["cast"][id]["job"] == "Director":
                            director += movie["cast"][id]["name"] + ", "
                    if director:
                        extended += _("Director: %s") % director[:-2]
                    if extended:
                        self["extended"].setText(extended)                     
            else:
                self["status"].setText(_("No data found at themoviedb.org!"))

        else:
            self["status"].setText(_("Error!\n%s" % errorString))

    def errorCoverDownload(self, error=None):
        if error is not None:
            print "[TMDb] Error: ", str(error.getErrorMessage())
        self["cover"].hide()

    def finishedCoverDownload(self, result, filename):
        self["cover"].updatecover(filename)
        
    def moviecoverPainted(self):
        self["cover"].show()

    def checkConnection(self):
        try:
            import socket 
            print socket.gethostbyname('www.google.com')
            return True
        except:
            self.session.openWithCallback(self.close, MessageBox, _("No internet connection available !"), MessageBox.TYPE_ERROR)
            return False

    def green_pressed(self):
        if self.checkConnection() == False:
            return
        from ServiceProvider import ServiceCenter
        from EventInformationTable import createEIT
        global movie_title
        movie_title = ServiceCenter.getInstance().info(self.service).getName(self.service).encode("utf-8")
        #current = self["list"].getCurrent()
        if self.service is not None: # and current:
            createEIT(self.service.getPath(), movie_title, config.AdvancedMovieSelection.coversize.value) #, movie=current[1])
            self.close(False)
        else:
            self.session.openWithCallback(self.close, MessageBox, _("Sorry, no info/cover found for title: %s") % (title), MessageBox.TYPE_ERROR)
