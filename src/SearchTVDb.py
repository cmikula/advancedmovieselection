#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  The plugin is developed on the basis from a lot of single plugins (thx for the code @ all)
#  Coded by JackDaniel & cmikula (c)2012
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
import urllib
import datetime
import re
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from enigma import getDesktop, iServiceInformation, eTimer
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from Components.ActionMap import ActionMap
from Components.GUIComponent import GUIComponent
from enigma import RT_WRAP, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, gFont, eListbox, eListboxPythonMultiContent
from Components.Label import Label
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ScrollLabel import ScrollLabel
from Tools.Directories import pathExists, fileExists
import os
from enigma import ePicLoad
from Components.AVSwitch import AVSwitch
from Components.ProgressBar import ProgressBar
from os import environ
from ServiceProvider import PicLoader, ServiceCenter
from EventInformationTable import createEITtvdb
import tvdb
import shutil

temp_dir = "/tmp/TheTVDB_temp/"

if environ["LANGUAGE"] == "de" or environ["LANGUAGE"] == "de_DE":
    nocover = ("/usr/lib/enigma2/python/Plugins/Extensions/AdvancedMovieSelection/images/nocover_de.png")
else:
    nocover = ("/usr/lib/enigma2/python/Plugins/Extensions/AdvancedMovieSelection/images/nocover_en.png")

if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/YTTrailer/plugin.pyo"):
    from Plugins.Extensions.YTTrailer.plugin import YTTrailerList
    YTTrailerPresent = True
else:
    YTTrailerPresent = False

def getImage(serie):
    thumb = serie['poster']
    if not thumb:
        thumb = serie['banner']
    if not thumb:
        thumb = serie['fanart']
    
    filename = None
    if thumb:
        thumb = thumb.encode('utf-8', 'ignore')
        filename = TheTVDBMain.htmlToFile(thumb)
        if filename and not os.path.exists(filename):
            urllib.urlretrieve(thumb, filename)

    if filename and os.path.exists(filename):
        return filename
    else:
        return nocover

class TheTVDBMainList(GUIComponent, object):
    def __init__(self):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.l.setBuildFunc(self.buildMovieSelectionListEntry)
        self.l.setFont(0, gFont("Regular", 24))
        self.l.setFont(1, gFont("Regular", 20))
        self.l.setItemHeight(140)
        self.picloader = PicLoader(95, 138)

    def buildMovieSelectionListEntry(self, movie, series_id):
        width = self.l.getItemSize().width()
        res = [ None ]
        
        serie = movie['Serie'][0]
        desc = serie['Overview']
        if desc:
            desc_txt = desc.encode('utf-8', 'ignore')
        else:
            desc_txt = _("Sorry, no description found at www.thetvdb.com!")
        name = serie['SeriesName'].encode('utf-8', 'ignore')
        id_txt = _("ID: %s") % series_id.encode('utf-8', 'ignore')
        
        filename = getImage(serie)
        png = self.picloader.load(filename)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 0, 1, 95, 138, png))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, 100, 2, width - 250 , 26, 0, RT_HALIGN_LEFT, "%s" % name))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, width - 255, 2, 250, 26, 0, RT_HALIGN_RIGHT, "%s" % id_txt))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, 100, 40, width - 100, 95, 1, RT_HALIGN_LEFT | RT_WRAP, "%s" % desc_txt))
        return res
        
    GUI_WIDGET = eListbox
    
    def postWidgetCreate(self, instance):
        instance.setContent(self.l)

    def preWidgetRemove(self, instance):
        instance.setContent(None)

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()

    def setList(self, _list):
        self.l.setList(_list)
    
    def getCurrent(self):
        return self.l.getCurrentSelection()

class EpisodesList(GUIComponent, object):
    def buildMovieSelectionListEntry(self, episode, episode_name, episode_number, episode_season_number, episode_id, episode_overview):
        width = self.l.getItemSize().width()
        res = [ None ]
        id = (_("ID: %s") % episode_id)
        season =  (_("Season: %s") % episode_season_number)
        episode_txt = (_("Episode: %s") % episode_number)
        res.append((eListboxPythonMultiContent.TYPE_TEXT, 5, 2, width - 250 , 23, 0, RT_HALIGN_LEFT, "%s" % episode_name))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, width - 255, 2, 250, 23, 0, RT_HALIGN_RIGHT, "%s" % id))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, 5, 27, width - 250 , 23, 0, RT_HALIGN_LEFT, "%s" % season))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, width - 255, 26, 250, 23, 0, RT_HALIGN_RIGHT, "%s" % episode_txt))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, 5, 52, width - 5, 79, 1, RT_HALIGN_LEFT | RT_WRAP, "%s" % episode_overview))
        return res
        
    def __init__(self):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.l.setBuildFunc(self.buildMovieSelectionListEntry)
        self.l.setFont(0, gFont("Regular", 20))
        self.l.setFont(1, gFont("Regular", 17))                               
        self.l.setItemHeight(140)
        self.picloader = PicLoader(95, 138)

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
                
class TheTVDBMain(Screen):
    def __init__(self, session, service, args=None):
        Screen.__init__(self, session)
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            self.skinName = ["TheTVDBMainHD"]
        elif sz_w == 1024:
            self.skinName = ["TheTVDBMainXD"]
        else:
            self.skinName = ["TheTVDBMainSD"]
        if not pathExists(temp_dir):
            os.mkdir(temp_dir, 0777)
        self.service = service
        info = ServiceCenter.getInstance().info(service)
        self.searchTitle = info.getName(service)
        self.description = info.getInfoString(service, iServiceInformation.sDescription)
        self["cover"] = Pixmap()
        self["cover"].hide()
        self["banner"] = Pixmap()
        self["banner"].hide()
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.paintPosterPixmapCB)
        self.picload2 = ePicLoad()
        self.picload2.PictureData.get().append(self.paintBannerPixmapCB)
        self["stars"] = ProgressBar()
        self["stars"].hide()
        self["no_stars"] = Pixmap()
        self["no_stars"].hide()
        self.ratingstars = -1
        self["description"] = ScrollLabel("")
        self["description"].hide()
        self["description_episode"] = ScrollLabel("")
        self["description_episode"].hide()
        self["extended"] = Label("")
        self["extended"].hide()
        self["extended_episode"] = Label("")
        self["extended_episode"].hide()
        self["button_red"] = Pixmap()
        self["button_red"].hide()
        self["button_green"] = Pixmap()
        self["button_green"].hide()
        self["button_yellow"] = Pixmap()
        self["button_yellow"].hide()
        self["button_blue"] = Pixmap()
        self["button_blue"].hide()
        self["status"] = Label("")
        self["status"].hide()
        self["result_txt"] = Label("")
        self["voted"] = Label("")
        self["voted"].hide()
        self["list"] = TheTVDBMainList()
        self["list"].hide()
        self["episodes_list"] = EpisodesList()
        self["episodes_list"].hide()
        self["seperator"] = Pixmap()
        self["seperator"].hide()
        self["setupActions"] = ActionMap([ "ColorActions", "DirectionActions", "SetupActions", "OkCancelActions" ],
        {
            "exit": self.cancel,
            "ok": self.blue_pressed,
            "red": self.red_pressed,
            "green": self.green_pressed,
            "blue": self.blue_pressed,
            "yellow": self.searchManual,
            "cancel": self.cancel,
            "upUp": self.pageUp,
            "leftUp": self.pageUp,
            "downUp": self.pageDown,
            "rightUp": self.pageDown,
        })
        self["key_red"] = StaticText("")
        self["key_green"] = StaticText("")
        self["key_yellow"] = StaticText("")
        self["key_blue"] = StaticText("")
        self.SearchCount = None
        self.EpisodeCount = None
        self.Result_list_lock_flag = None
        self.Show_Details_lock_flag = None
        self.Episodes_lock_flag = None
        self.Episode_Details_lock_flag = None
        self.timer = eTimer()
        self.timer.callback.append(self.getSeriesList)
        self.onLayoutFinish.append(self.layoutFinished)
        self.onClose.append(self.deleteTempDir)
        self.startSearch()

    def layoutFinished(self):
        sc = AVSwitch().getFramebufferScale()
        self.picload.setPara((self["cover"].instance.size().width(), self["cover"].instance.size().height(), sc[0], sc[1], False, 1, "#00000000"))
        self.picload2.setPara((self["banner"].instance.size().width(), self["banner"].instance.size().height(), sc[0], sc[1], False, 1, "#00000000"))

    def startSearch(self):
        self.setTitle(_("TheTVDB.com Info & D/L"))
        self["status"].setText(_("Searching for ' %s ' on TheTVDB.com, please wait ...") % self.searchTitle)
        self["status"].show()
        self.timer.start(100, True)
    
    def pageUp(self):
        self["description"].pageUp()
        self["description_episode"].pageUp()

    def pageDown(self):
        self["description"].pageDown()
        self["description_episode"].pageDown()

    def deleteTempDir(self):
        try:
            shutil.rmtree(temp_dir)
        except Exception, e:
            print "[AdvancedMovieSelection] ERROR deleting:", temp_dir
            print e

    def cancel(self):
        self.close(False)

    def getSeriesList(self):
        self.Result_list_lock_flag = True
        self.Show_Details_lock_flag = False
        self.Episodes_lock_flag = False
        self.Episode_Details_lock_flag = False
        searchTitle = self.searchTitle
        self.setTitle(_("TheTVDB.com Info for: %s") % searchTitle)
        results = tvdb.search(searchTitle)
        tmpList = []
        if len(results) > 0:
            try:
                for searchResult in results:
                    movie = tvdb.getMovieInfo(searchResult['id'])
                    _id = movie['Serie'][0]['id']
                    tmpList.append((movie, _id),)
            except Exception, e:
                print e
        if len(tmpList) > 0:
            self["list"].setList(tmpList)
            self["list"].show()
            self.SearchCount = 0 
            for x in tmpList:
                if x:
                    self.SearchCount = self.SearchCount + 1
            if self.SearchCount == 1:
                txt = (_("Total %s") % self.SearchCount + ' ' + _("show found"))
            else:
                txt = (_("Total %s") % self.SearchCount + ' ' + _("shows found"))
            self["result_txt"].setText(txt)   
            self["seperator"].show()
            #self["result_txt"].setText(_("Search results:"))            
            self["key_red"].setText(_("Info/Cover save"))
            self["button_red"].show()
            self["button_green"].show()
            self["key_green"].setText(_("Display show details"))
            self["key_yellow"].setText(_("Manual search"))
            self["button_yellow"].show()
            self["key_blue"].setText(_("Display episodes list"))
            self["button_blue"].show()
            self["status"].hide()
        else:
            if " - " in searchTitle:
                self.searchTitle = searchTitle.split(" - ")[0].strip()
                self.getSeriesList()
            else:
                self["result_txt"].setText("")
                self["result_txt"].hide()
                self["button_red"].hide()
                self["button_green"].hide()
                self["key_yellow"].setText(_("Manual search"))
                self["button_yellow"].show()
                self["button_blue"].hide()
                self["status"].setText(_("Sorry, no data found at TheTVDB.com!"))
                self["status"].show()

    def getEpisodeList(self):
        self.Result_list_lock_flag = False
        self.Show_Details_lock_flag = False
        self.Episodes_lock_flag = True
        self.Episode_Details_lock_flag = False
        searchTitle = self.searchTitle
        self.setTitle(_("Episodes for: %s") % searchTitle)
        results = tvdb.search(searchTitle)
        tmpEpisodeList = []
        if len(results) > 0:
            try:
                for searchResult in results:
                    movie = tvdb.getMovieInfo(searchResult['id'])
                    for episode in movie['Episode']:
                        if episode:
                            episode_name = ""
                            name = episode['EpisodeName']
                            if name:
                                episode_name = name.encode('utf-8', 'ignore')
                            episode_number = episode['EpisodeNumber']
                            if episode_number:
                                episode_number = episode_number.encode('utf-8', 'ignore') 
                            season_number = episode['SeasonNumber']
                            if season_number:
                                episode_season_number = season_number.encode('utf-8', 'ignore')
                            id = episode['id']
                            if id:
                                episode_id = id.encode('utf-8', 'ignore')
                            episode_overview = ""
                            overview = episode['Overview']
                            if overview:
                                episode_overview = str(overview).encode('utf-8', 'ignore')
                            else:
                                episode_overview = (_("Sorry, no description for this episode at TheTVDB.com available!"))
                            tmpEpisodeList.append((episode, episode_name, episode_number, episode_season_number, episode_id, episode_overview),)
            except Exception, e:
                print e
        if len(tmpEpisodeList) > 0:
            self["seperator"].show()
            self["extended_episode"].hide()
            self["banner"].hide()
            self["cover"].hide()
            self["list"].hide()
            self["description"].hide()
            self["voted"].hide()
            self["stars"].hide()
            self["no_stars"].hide()
            self["extended"].hide()
            self["episodes_list"].setList(tmpEpisodeList)
            self["episodes_list"].show()
            self.EpisodeCount = 0 
            for x in tmpEpisodeList:
                if x:
                    self.EpisodeCount = self.EpisodeCount + 1
            if self.SearchCount == 1:
                txt = (_("Total %s") % self.EpisodeCount + ' ' + _("episode found"))
            else:
                txt = (_("Total %s") % self.EpisodeCount + ' ' + _("episodes found"))
            self["result_txt"].setText(txt)
            #self["result_txt"].setText(_("Episodes overview:"))
            self["result_txt"].show()
            self["button_green"].show()
            self["key_green"].setText(_("Display show details"))
            self["key_blue"].setText(_("Display episodes details"))
            self["button_blue"].show()
            self["description_episode"].hide()

    def getEpisodeDetails(self, movie):
        self.Result_list_lock_flag = False
        self.Show_Details_lock_flag = False
        self.Episodes_lock_flag = False
        self.Episode_Details_lock_flag = True
        if movie:
            name = movie["EpisodeName"].encode('utf-8', 'ignore')
            self.setTitle(_("Episodes Details for: %s") % name + ' / ' + self.searchTitle)
            try:
                overview = ""
                overview = movie['Overview']
                if overview:
                    overview = str(overview).encode('utf-8', 'ignore')
                else:
                    overview = (_("Sorry, no description for this episode at TheTVDB.com available!"))          
                extended = ""
                director = ""
                director = movie["Director"]
                if director:
                    director = director.replace("|", ", ")
                    extended = (_("Regie: %s") % director.encode('utf-8', 'ignore')) + ' / '
                writer = ""
                writer = movie["Writer"]
                if writer:
                    writer = writer.replace("|", ", ")
                    extended += (_("Writer: %s\n") % writer.encode('utf-8', 'ignore'))
                guest_stars = ""
                guest_stars = movie["GuestStars"]
                if guest_stars:
                    if guest_stars.startswith("|"):
                        guest_stars = guest_stars[1:-1].replace("|", ", ")
                    else:
                        guest_stars = guest_stars.replace("|", ", ")
                    extended += (_("Guest Stars: %s\n") % guest_stars.encode('utf-8','ignore'))
                first_aired = ""
                first_aired = movie["FirstAired"]
                if first_aired:
                    extended += (_("First Aired: %s") % first_aired.encode('utf-8','ignore'))
                image= ""
                image = movie["filename"]
                if image:
                    cover_file = self.downloadBanner(image)
                    self.setBanner(cover_file)
                else:
                    cover_file = ""
                    self.setBanner(cover_file)
                self["seperator"].show()
                self["banner"].show()
                self["cover"].hide()
                self["description_episode"].setText(overview)
                self["description_episode"].show()
                self["episodes_list"].hide()
                self["result_txt"].hide()
                self["extended_episode"].setText(extended)
                self["extended_episode"].show()
                self["key_blue"].setText(_("Display episodes list"))
            except Exception, e:
                print e

    def searchManual(self):
        self.session.openWithCallback(self.newSearchCallback, VirtualKeyBoard, title=_("Enter new movie name for search:"), text=self.searchTitle)        

    def newSearchCallback(self, text=None):
        if text:
            self.searchTitle = text
            self.startSearch()

    def getMovieInfo(self, movie):
        self.Result_list_lock_flag = False
        self.Show_Details_lock_flag = True
        self.Episodes_lock_flag = False
        self.Episode_Details_lock_flag = False
        self.setTitle(_("Details for: %s") % self.searchTitle)
        serie = movie['Serie'][0]
        try:
            serie_name = serie['SeriesName'].encode('utf-8', 'ignore')
            overview = serie['Overview']
            if overview:
                overview = overview.encode('utf-8', 'ignore')
            else:
                overview = _("Sorry, no description for ' %s ' at TheTVDB.com found!") % self.name
            
            cover_file = self.downloadCover(serie)
            self.setPoster(cover_file)
            self["seperator"].show()
            self["banner"].hide()
            self["description_episode"].hide()
            self["extended_episode"].hide()
            self["status"].hide()
            self["list"].hide()
            if YTTrailerPresent:
                self["button_green"].show()
                self["key_green"].setText(_("Trailer search"))
            else:
                self["button_green"].hide()
                self["key_green"].setText("")
            self["button_blue"].show()
            self["result_txt"].hide()
            self["list"].hide()
            self["description"].show()
            self["description"].setText(overview)
            self["voted"].show()
            self["episodes_list"].hide()
            self["key_blue"].setText(_("Display episodes list"))
            self["button_blue"].show()
            self["description_episode"].hide()
    
            extended = ""
            first_aired = TheTVDBMain.convert_date(serie['FirstAired']) 
            if first_aired: 
                extended = (_("First Aired: %s") % first_aired) + ' / '
    
            airs_day = serie['Airs_DayOfWeek']
            if airs_day:
                extended += (_("Air Day: %s") % airs_day.encode('utf-8', 'ignore')) + ' / '
            else:
                extended += ""
    
            airs_time = TheTVDBMain.convert_time(serie['Airs_Time'])
            if airs_time:
                extended += (_("Air Time: %s") % airs_time) + ' / '
            
            runtime = serie['Runtime']
            if runtime:
                extended += (_("Runtime: %s minutes\n") % runtime.encode('utf-8', 'ignore'))
    
            network = serie['Network']
            if network:
                extended += (_("Broadcast TV network: %s") % network.encode('utf-8', 'ignore')) + ' / '
            else:
                extended += ""
            
            if serie['Genre']:
                genre = " ,".join(serie['Genre'])
                extended += (_("Genre: %s\n") % str(genre).encode('utf-8', 'ignore'))
                
            content_rating = serie['ContentRating']
            if content_rating:
                extended += (_("Certification: %s") % content_rating.encode('utf-8', 'ignore')) + ' / '
    
            rating = serie['Rating']
            if rating:
                rating = rating.encode('utf-8', 'ignore')
                self.ratingstars = int(10 * round(float(rating.replace(',', '.')), 1))
                self["stars"].show()
                self["stars"].setValue(self.ratingstars)
                self["no_stars"].show()
                extended += (_("Rating: %s\n") % rating)
    
            if serie['Actors']:
                genre = " ,".join(serie['Actors']).encode('utf-8', 'ignore')
                extended += (_("Actors: %s\n") % genre)
    
            last_updated = serie['lastupdated']
            if last_updated is not None:
                last_updated = datetime.datetime.fromtimestamp(int(last_updated))
                extended += (_("\nLast modified at TheTVDB.com: %s") % last_updated)
    
            if extended:
                self["extended"].show()
                self["extended"].setText(extended)
            
            user_rating = serie['RatingCount']
            if user_rating:
                self["voted"].setText(_("Voted: %s") % user_rating.encode('utf-8', 'ignore') + ' ' + _("times"))
            else:
                self["voted"].setText(_("No user voted!"))
    
        except Exception, e:
            print e

    def downloadBanner(self, image):
        if image:
            filename = self.htmlToFile(image)
            if filename and not os.path.exists(filename):
                urllib.urlretrieve(image, filename)
            return filename

    def setBanner(self, filename):
        if not filename or not os.path.exists(filename):
            filename = nocover
        self.picload2.startDecode(filename)

    def paintBannerPixmapCB(self, picInfo=None):
        ptr = self.picload2.getData()
        if ptr != None:
            self["banner"].instance.setPixmap(ptr.__deref__())
            self["banner"].show()

    def downloadCover(self, serie):
        thumb = serie['poster']
        if thumb:
            filename = self.htmlToFile(thumb)
            if filename and not os.path.exists(filename):
                urllib.urlretrieve(thumb, filename)
            return filename
    
    def setPoster(self, filename):
        if not filename or not os.path.exists(filename):
            filename = nocover
        self.picload.startDecode(filename)

    def paintPosterPixmapCB(self, picInfo=None):
        ptr = self.picload.getData()
        if ptr != None:
            self["cover"].instance.setPixmap(ptr.__deref__())
            self["cover"].show()
            
    @staticmethod
    def convert_time(time_string):
        """Convert a thetvdb time string into a datetime.time object."""
        time_res = [re.compile(r"\D*(?P<hour>\d{1,2})(?::(?P<minute>\d{2}))?.*(?P<ampm>a|p)m.*", re.IGNORECASE),
                    re.compile(r"\D*(?P<hour>\d{1,2}):?(?P<minute>\d{2}).*")]                                     
        for r in time_res:
            m = r.match(time_string.encode('utf-8', 'ignore'))
            if m:
                gd = m.groupdict()
                if "hour" in gd and "minute" in gd and gd["minute"] and "ampm" in gd:
                    hour = int(gd["hour"])
                    if gd["ampm"].lower() == "p":
                        hour += 12
                    return datetime.time(hour, int(gd["minute"]))
                elif "hour" in gd and "ampm" in gd:
                    hour = int(gd["hour"])
                    if gd["ampm"].lower() == "p":
                        hour += 12
                    return datetime.time(hour, 0)
                elif "hour" in gd and "minute" in gd:
                    return datetime.time(int(gd["hour"]), int(gd["minute"]))
        return None

    @staticmethod
    def convert_date(date_string):
        """Convert a thetvdb date string into a datetime.date object."""
        first_aired = None
        try:
            first_aired = datetime.date(*map(int, date_string.encode('utf-8', 'ignore').split("-")))
        except Exception, e:
            print e
        return first_aired
        
    @staticmethod
    def htmlToFile(address):
        if address:
            return temp_dir + address.split("/")[-1]

    def checkConnection(self):
        try:
            import socket 
            print socket.gethostbyname('www.google.com')
            return True
        except:
            self.session.openWithCallback(self.close, MessageBox, _("No internet connection available!"), MessageBox.TYPE_ERROR)
            return False

    def red_pressed(self):
        cur = self["list"].getCurrent()
        if not self.checkConnection() or not cur:
            return
        current_movie = cur[0]['Serie'][0]
        title = current_movie['SeriesName'].encode('utf-8', 'ignore')
        if self.service is not None:
            createEITtvdb(self.service.getPath(), title, serie=current_movie)
            self.close(False)
        else:
            self.session.openWithCallback(self.close, MessageBox, _("Sorry, no info/cover found for title: %s") % (title), MessageBox.TYPE_ERROR)
            
# TODO: rewrite method conditions
    def green_pressed(self):
        if self.Result_list_lock_flag and not self.Show_Details_lock_flag and not self.Episodes_lock_flag and not self.Episode_Details_lock_flag:
            # TODO: duplicate code segment (check condition and join delow code)
            cur = self["list"].getCurrent()
            if cur is not None:
                self["list"].hide()
                self["status"].setText(_("Getting movie information for '%s' from TMDb...") % cur[1].encode('utf-8', 'ignore'))
                self["status"].show()
                self.getMovieInfo(cur[0])
        elif not self.Result_list_lock_flag and not self.Show_Details_lock_flag and self.Episodes_lock_flag or self.Episode_Details_lock_flag:
            # TODO: duplicate code segment
            cur = self["list"].getCurrent()
            if cur is not None:
                self["list"].hide()
                self["status"].setText(_("Getting movie information for '%s' from TMDb...") % cur[1].encode('utf-8', 'ignore'))
                self["status"].show()
                self.getMovieInfo(cur[0])      
        elif YTTrailerPresent and not self.Result_list_lock_flag and self.Show_Details_lock_flag and not self.Episodes_lock_flag and not self.Episode_Details_lock_flag:
            eventname = self.searchTitle
            self.session.open(YTTrailerList, eventname) 

# TODO: rewrite method conditions                
    def blue_pressed(self):
        if self.Result_list_lock_flag and not self.Show_Details_lock_flag and not self.Episodes_lock_flag and not self.Episode_Details_lock_flag:
            # TODO: duplicate code segment (check and rewrite condition and ensure to call only once this method)
            self.getEpisodeList()
        elif not self.Result_list_lock_flag and self.Show_Details_lock_flag and not self.Episodes_lock_flag and not self.Episode_Details_lock_flag:
            # TODO: duplicate code segment
            self.getEpisodeList()
        elif not self.Result_list_lock_flag and not self.Show_Details_lock_flag and not self.Episodes_lock_flag and self.Episode_Details_lock_flag:
            # TODO: duplicate code segment
            self.getEpisodeList()
        elif not self.Result_list_lock_flag and not self.Show_Details_lock_flag and self.Episodes_lock_flag and not self.Episode_Details_lock_flag:
            cur = self["episodes_list"].getCurrent()
            if cur is not None:
                self.getEpisodeDetails(cur[0])