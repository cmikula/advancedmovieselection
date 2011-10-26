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
from enigma import ePicLoad
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.AVSwitch import AVSwitch
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.config import config
from shutil import rmtree as shutil_rmtree
from enigma import getDesktop
import tmdb, urllib

tmdb_logodir = "/usr/lib/enigma2/python/Plugins/Extensions/AdvancedMovieSelection/images"
IMAGE_TEMPFILE = "/tmp/cover_temp"

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
            print "No Cover found for", str(name), "\n"
        else:    
            parts = cover_url.split("/")
            filename = os_path.join(IMAGE_TEMPFILE , id + parts[-1])
            urllib.urlretrieve(cover_url, filename)
            png = LoadPixmap(cached=True, path=filename)
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 0, 1, 92, 138, png))

        res.append((eListboxPythonMultiContent.TYPE_TEXT, 100, 5, width - 100 , 20, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, "%s" % name.encode('utf-8', 'ignore')))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, width - 140, 5, 130 , 20, 1, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, "%s" % released_text))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, 100, 30, width - 100, 100, 1, RT_WRAP, "%s" % overview))
        return res
        
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
        self.onFirstExecBegin.append(self.searchForMovies)

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
        self["key_green"].text = ""
        self["key_blue"].text = ""
        
        try:
            results = tmdb.search(self.searchTitle)
            # If no result found, Split the search title before " - " and search again 
            if len(results) == 0 and " - " in self.searchTitle:
                title = self.searchTitle.split(" - ")[0].strip()
                results = tmdb.search(title)
                if len(results) > 0:
                    self.searchTitle = title

            if len(results) == 0:
                self["status"].setText(_("No data found at themoviedb.org!"))
                self.session.openWithCallback(self.askForSearchCallback, MessageBox, _("No data found at themoviedb.org!\nDo you want to edit the search name?"))
                return
            
            self["key_green"].text = _("Save movie info/cover")
            self["key_blue"].text = _("Extended Info")
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
            self.getMovieInfo(cur[0])

    def getMovieInfo(self, movie):
        if movie:
            self["status"].hide()
            self["list"].hide()
            self["key_blue"].text = _("Extended Info")
            self["key_green"].text = ""
            self["key_green"].text = _("Save movie info/cover")
            self["key_yellow"].text = _("Manual search")
            self["description"].show()
            self["extended"].show()

            extended = ""
            name = movie["name"].encode('utf-8', 'ignore')
            description = movie["overview"]
            released = movie["released"]
            self.setTitle(_("TMDb movie info for: %s") % name)
            if description:
                description_text = description.encode('utf-8', 'ignore')
                self["description"].setText(name + "\n\n" + description_text)
            else:
                self["description"].setText(name)
            
            cover_url = None
            images = movie['images']
            if len(images) > 0:
                cover_url = images[0]['thumb']
            if not cover_url:
                print "No Cover found for", str(name), "\n"
            else:    
                parts = cover_url.split("/")
                filename = os_path.join(IMAGE_TEMPFILE , movie['id'] + parts[-1])
                if os_path.exists(filename):
                    self["cover"].updatecover(filename)

            if released:
                extended = (_("Appeared: %s\n") % released)
            
            if movie.has_key('categories') and movie['categories'].has_key('genre'):                      
                categories = []
                for genre in movie['categories']['genre']:
                    categories.append(genre)
                if len(categories) > 0:
                    extended += _("Genre: %s\n") % ", ".join(categories) 
            
            if movie.has_key('studios'):
                studios = []
                for studio in movie["studios"]:
                    studios.append(studio)
                if len(studios) > 0:
                    extended += _("Studio: %s\n") % ", ".join(studios)
                else:
                    extended += "\n"
            
            if movie.has_key('cast') and movie['cast'].has_key('producer'):                      
                director = []
                for prodr in movie['cast']['producer']:
                    director.append(prodr['name'])
                if len(director) > 0:
                    extended += _("Director: %s") % ", ".join(director)

            if extended:
                self["extended"].setText(extended)                     

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
