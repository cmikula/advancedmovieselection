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
from enigma import ePoint
from Screens.Screen import Screen
from RecordPaths import RecordPathsSettings
from About import AdvancedMovieSelectionAbout
from Components.Pixmap import Pixmap
from Components.PluginComponent import plugins
from Plugins.Plugin import PluginDescriptor
from Components.config import config, ConfigSelection, getConfigListEntry, configfile
from Components.Sources.StaticText import StaticText
from Components.Button import Button
from Components.ConfigList import ConfigListScreen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.LocationBox import MovieLocationBox
from Components.UsageConfig import preferredPath
from Screens.MessageBox import MessageBox
from MessageBoxEx import MessageBoxEx
from Components.Sources.List import List
from Components.ActionMap import ActionMap
from enigma import getDesktop, quitMainloop
from Tools.Directories import fileExists

if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/IMDb/plugin.pyo"):
    IMDbPresent = True
else:
    IMDbPresent = False
if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/OFDb/plugin.pyo"):
    OFDbPresent = True
else:
    OFDbPresent = False
if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/TMDb/plugin.pyo"):
    TMDbPresent = True
else:
    TMDbPresent = False
if fileExists("/usr/lib/enigma2/python/Plugins/Bp/geminimain/plugin.pyo"):
    GP3Present = True
else:
    GP3Present = False
if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/YTTrailer/plugin.pyo"):
    YTTrailerPresent=True
else:
    YTTrailerPresent=False

class AdvancedMovieSelectionSetup(ConfigListScreen, Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            self.skinName = ["AdvancedMovieSelectionSetupHD"]
        elif sz_w == 1024:
            self.skinName = ["AdvancedMovieSelectionSetupXD"]
        else:
            self.skinName = ["AdvancedMovieSelectionSetupSD"]
        self.session = session        
        self.OnOff = None
        self.Startwith = None
        self.StartDir = None
        self.StartFirst = None
        self.ShowMenu = None
        self.ShowSetup = None
        self.Showextras = None
        self.ShowSort = None
        self.ShowMark = None
        self.ShowDel = None
        self.ShowMove = None
        self.ShowSearch = None
        self.ShowPreview = None
        self.Coversize = None
        self.ShowDelInfoCover = None
        self.ShowDelCover = None
        self.ShowDelInfo = None
        self.ShowRename = None
        self.ShowTMDb = None
        self.AskDelete = None
        self.Percentmark = None
        self.ShowListstyle = None
        self.MovieLength = None
        self.AskEventinfo = None
        self.Eventinfotyp = None
        self.Eventinfotyp2 = None
        self.Eventinfotyp3 = None
        self.Eventinfotyp4 = None
        self.Eventinfotyp5 = None
        self.Eventinfotyp6 = None
        self.Eventinfotyp7 = None
        self.ShowColorkeys = None
        self.ShowCoverOptions = None
        self.MovieStart = None
        self.MovieStop = None
        self.MovieEnd = None
        self.ShowMoviebarPosition = None
        self.Color1 = None
        self.Color2 = None
        self.Color3 = None
        self.Dateformat = None
        self.Shownew = None
        self.MiniTV = None
        self.UseFolderName = None
        self.Jump2Mark = None
        self.ShowMovieTagsinMenu = None
        self.ShowFilterbyTags = None
        self.ShowTrailer = None
        self.needsRestartFlag = False
        self.needsReopenFlag = False
        self["setupActions"] = ActionMap(["ColorActions", "OkCancelActions", "MenuActions", "EPGSelectActions"],
        {
            "ok":       self.keySave,
            "cancel":   self.keyCancel,
            "red":      self.keyCancel,
            "green":    self.keySave,
            "yellow":   self.buttonsetup,
            "blue":     self.RecPathSettings,
            "info":     self.about,
        }, -2)
        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session)
        self["key_red"] = StaticText(_("Close"))
        self["key_green"] = StaticText(_("Save"))
        self["key_yellow"] = StaticText(_("Color key settings"))
        self["key_blue"] = StaticText(_("Default paths"))
        self["help"] = StaticText("")
        self["Trailertxt"] = StaticText("")
        self["TMDbtxt"] = StaticText("")
        self["IMDbtxt"] = StaticText("")
        self["OFDbtxt"] = StaticText("")
        self.onShown.append(self.setWindowTitle)
        self.createSetup()
        self.pluginsavailable()

    def setWindowTitle(self):
        self.setTitle(_("Advanced Movie Selection Setup"))

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.createSetup()
        if config.AdvancedMovieSelection.ml_disable.isChanged():
            self.needsRestartFlag = True
        elif config.AdvancedMovieSelection.movie_launch.isChanged():
            self.needsRestartFlag = True
        elif config.AdvancedMovieSelection.showpreview.isChanged():
            self.needsReopenFlag = True
        elif config.usage.load_length_of_movies_in_moviellist.isChanged() and config.usage.load_length_of_movies_in_moviellist.value == False:
            config.AdvancedMovieSelection.showprogessbarinmovielist.value = False
            config.AdvancedMovieSelection.showiconstatusinmovielist.value = False
            config.AdvancedMovieSelection.showcolorstatusinmovielist.value = False
        elif config.AdvancedMovieSelection.color1.isChanged() or config.AdvancedMovieSelection.color2.isChanged() or config.AdvancedMovieSelection.color3.isChanged(): 
            self.needsReopenFlag = True
        elif config.AdvancedMovieSelection.minitv.isChanged():
            self.needsReopenFlag = True

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.createSetup()
        if config.AdvancedMovieSelection.ml_disable.isChanged():
            self.needsRestartFlag = True
        elif config.AdvancedMovieSelection.movie_launch.isChanged():
            self.needsRestartFlag = True
        elif config.AdvancedMovieSelection.showpreview.isChanged():
            self.needsReopenFlag = True
        elif config.usage.load_length_of_movies_in_moviellist.isChanged() and config.usage.load_length_of_movies_in_moviellist.value == False:
            config.AdvancedMovieSelection.showprogessbarinmovielist.value = False
            config.AdvancedMovieSelection.showiconstatusinmovielist.value = False
            config.AdvancedMovieSelection.showcolorstatusinmovielist.value = False
        elif config.AdvancedMovieSelection.color1.isChanged() or config.AdvancedMovieSelection.color2.isChanged() or config.AdvancedMovieSelection.color3.isChanged():
            self.needsReopenFlag = True
        elif config.AdvancedMovieSelection.minitv.isChanged():
            self.needsReopenFlag = True

    def createSetup(self):
        self.list = []
        self.OnOff = getConfigListEntry(_("Disable Advanced Movie Selection:"), config.AdvancedMovieSelection.ml_disable)
        self.Startwith = getConfigListEntry(_("Start Advanced Movie Selection with:"), config.AdvancedMovieSelection.movie_launch)
        self.StartDir = getConfigListEntry(_("Start on last movie location:"), config.AdvancedMovieSelection.startdir)
        self.StartFirst = getConfigListEntry(_("Start on first position in movielist:"), config.AdvancedMovieSelection.startonfirst)
        self.ShowMenu = getConfigListEntry(_("Show plugin config in extensions menu from movielist:"), config.AdvancedMovieSelection.showmenu)
        self.ShowColorkeys = getConfigListEntry(_("Show color key setup in extensions menu from movielist:"), config.AdvancedMovieSelection.showcolorkey)
        self.ShowSetup = getConfigListEntry(_("Show movie plugins in extensions menu from movielist:"), config.AdvancedMovieSelection.pluginmenu_list)
        self.Showextras = getConfigListEntry(_("Show list options in extensions menu from movielist:"), config.AdvancedMovieSelection.showextras)
        self.ShowSort = getConfigListEntry(_("Show sort options in extensions menu from movielist:"), config.AdvancedMovieSelection.showsort)
        self.ShowListstyle = getConfigListEntry(_("Show list styles in extensions menu from movielist:"), config.AdvancedMovieSelection.showliststyle)
        self.ShowMark = getConfigListEntry(_("Show mark movie in extensions menu from movielist:"), config.AdvancedMovieSelection.showmark)
        self.ShowDel = getConfigListEntry(_("Show delete option in extensions menu from movielist:"), config.AdvancedMovieSelection.showdelete)
        self.ShowMove = getConfigListEntry(_("Show move/copy option in extensions menu from movielist:"), config.AdvancedMovieSelection.showmove)
        self.ShowSearch = getConfigListEntry(_("Show movie search in extensions menu from movielist:"), config.AdvancedMovieSelection.showsearch)
        self.ShowPreview = getConfigListEntry(_("Show covers in movielist:"), config.AdvancedMovieSelection.showpreview)
        self.Coversize = getConfigListEntry(_("Set coversize:"), config.AdvancedMovieSelection.coversize)
        self.ShowCoverOptions = getConfigListEntry(_("Show D/L and store info/cover in movielist extensions menu:"), config.AdvancedMovieSelection.showcoveroptions)
        self.ShowDelInfoCover = getConfigListEntry(_("Show delete info and cover in extensions menu from movielist:"), config.AdvancedMovieSelection.show_info_cover_del)
        self.ShowDelCover = getConfigListEntry(_("Show delete cover in extensions menu from movielist:"), config.AdvancedMovieSelection.show_cover_del)
        self.ShowDelInfo = getConfigListEntry(_("Show delete movie info in extensions menu from movielist:"), config.AdvancedMovieSelection.show_info_del)      
        self.ShowRename = getConfigListEntry(_("Show rename in extensions menu from movielist:"), config.AdvancedMovieSelection.showrename)
        self.ShowTMDb = getConfigListEntry(_("Show TMDb search in extensions menu from movielist:"), config.AdvancedMovieSelection.showtmdb)
        self.Jump2Mark = getConfigListEntry(_("Jump to first mark when starts playing movie:"), config.AdvancedMovieSelection.jump_first_mark)
        self.ShowMovieTagsinMenu = getConfigListEntry(_("Show movie tags in extensions menu from movielist:"), config.AdvancedMovieSelection.showmovietagsinmenu)
        self.ShowFilterbyTags = getConfigListEntry(_("Show filter by tags in extensions menu from movielist:"), config.AdvancedMovieSelection.showfiltertags)
        self.ShowTrailer = getConfigListEntry(_("Show search trailer on web in extensions menu from movielist:"), config.AdvancedMovieSelection.showtrailer)
        self.MovieLength = getConfigListEntry(_("Load Length of Movies in Movielist:"), config.usage.load_length_of_movies_in_moviellist)
        self.Percentmark = getConfigListEntry(_("Mark movie as seen at position (in percent):"), config.AdvancedMovieSelection.moviepercentseen)
        self.AskDelete = getConfigListEntry(_("Ask before delete:"), config.AdvancedMovieSelection.askdelete)
        if IMDbPresent and OFDbPresent and TMDbPresent:
            self.Eventinfotyp = getConfigListEntry(_("INFO button function:"), config.AdvancedMovieSelection.Eventinfotyp)
        else:
            if IMDbPresent and not OFDbPresent and not TMDbPresent:
                self.Eventinfotyp2 = getConfigListEntry(_("INFO button function:"), config.AdvancedMovieSelection.Eventinfotyp2) 
            else:
                if OFDbPresent and not TMDbPresent and not IMDbPresent:
                    self.Eventinfotyp3 = getConfigListEntry(_("INFO button function:"), config.AdvancedMovieSelection.Eventinfotyp3) 
                else:
                    if TMDbPresent and not OFDbPresent and not IMDbPresent:
                        self.Eventinfotyp4 = getConfigListEntry(_("INFO button function:"), config.AdvancedMovieSelection.Eventinfotyp4)
                    else:
                        if TMDbPresent and not OFDbPresent and IMDbPresent:
                            self.Eventinfotyp5 = getConfigListEntry(_("INFO button function:"), config.AdvancedMovieSelection.Eventinfotyp5)
                        else:
                            if TMDbPresent and OFDbPresent and not IMDbPresent:
                                self.Eventinfotyp6 = getConfigListEntry(_("INFO button function:"), config.AdvancedMovieSelection.Eventinfotyp6) 
                            else:
                                if not TMDbPresent and OFDbPresent and IMDbPresent:
                                    self.Eventinfotyp7 = getConfigListEntry(_("INFO button function:"), config.AdvancedMovieSelection.Eventinfotyp7)
        self.MovieStart = getConfigListEntry(_("Behavior when a movie is started:"), config.usage.on_movie_start)
        self.MovieStop = getConfigListEntry(_("Behavior when a movie is stopped:"), config.usage.on_movie_stop)
        self.MovieEnd = getConfigListEntry(_("Behavior when a movie reaches the end:"), config.usage.on_movie_eof)
        self.ShowMoviebarPosition = getConfigListEntry(_("Show Moviebar position setup in extensions menu from movielist:"), config.AdvancedMovieSelection.show_infobar_position)
        self.Color1 = getConfigListEntry(_("Color for not ready seen movies:"), config.AdvancedMovieSelection.color1)
        self.Color2 = getConfigListEntry(_("Color for ready seen movies:"), config.AdvancedMovieSelection.color2)
        self.Color3 = getConfigListEntry(_("Color for recording movies:"), config.AdvancedMovieSelection.color3)
        self.Dateformat = getConfigListEntry(_("Assign the date format for movielist:"), config.AdvancedMovieSelection.dateformat)
        self.Shownew = getConfigListEntry(_("Show new recordings icon:"), config.AdvancedMovieSelection.shownew)
        self.MiniTV = getConfigListEntry(_("Show Mini TV:"), config.AdvancedMovieSelection.minitv)
        self.UseFolderName = getConfigListEntry(_("Use folder name for display covers:"), config.AdvancedMovieSelection.usefoldername)
        self.list.append(self.OnOff)
        self.list.append(self.Startwith)
        self.list.append(self.StartDir)
        self.list.append(self.StartFirst)
        self.list.append(self.ShowMenu)
        self.list.append(self.ShowColorkeys)
        self.list.append(self.ShowSetup)
        if config.usage.load_length_of_movies_in_moviellist.value:
            self.list.append(self.Showextras)
        self.list.append(self.ShowSort)
        self.list.append(self.ShowListstyle)
        if config.usage.load_length_of_movies_in_moviellist.value:
            self.list.append(self.ShowMark)
        self.list.append(self.ShowDel)
        self.list.append(self.ShowMove)
        self.list.append(self.ShowSearch)
        self.list.append(self.ShowPreview)
        if config.AdvancedMovieSelection.showpreview.value:
            self.list.append(self.Coversize)
            self.list.append(self.UseFolderName)
            self.list.append(self.ShowCoverOptions)
            self.list.append(self.ShowDelInfoCover)
            self.list.append(self.ShowDelCover)
            self.list.append(self.ShowDelInfo)
        self.list.append(self.ShowRename)
        self.list.append(self.ShowTMDb)
        self.list.append(self.ShowMovieTagsinMenu)
        self.list.append(self.ShowFilterbyTags)
        self.list.append(self.ShowTrailer)
        self.list.append(self.MovieLength)
        if config.usage.load_length_of_movies_in_moviellist.value:
            self.list.append(self.Percentmark)
        self.list.append(self.AskDelete)
        if IMDbPresent and OFDbPresent and TMDbPresent:
            self.list.append(self.Eventinfotyp)
        else:
            if IMDbPresent and not OFDbPresent and not TMDbPresent:
                self.list.append(self.Eventinfotyp2)
            else:
                if OFDbPresent and not IMDbPresent and not TMDbPresent:
                    self.list.append(self.Eventinfotyp3)
                else:
                    if TMDbPresent and not OFDbPresent and not IMDbPresent:
                        self.list.append(self.Eventinfotyp4)
                    else:
                        if TMDbPresent and not OFDbPresent and IMDbPresent:
                            self.list.append(self.Eventinfotyp5)
                        else:
                            if TMDbPresent and OFDbPresent and not IMDbPresent:
                                self.list.append(self.Eventinfotyp6)
                            else:
                                if not TMDbPresent and OFDbPresent and IMDbPresent:
                                    self.list.append(self.Eventinfotyp7)
        self.list.append(self.MovieStart)
        self.list.append(self.MovieStop)
        self.list.append(self.MovieEnd)
        self.list.append(self.ShowMoviebarPosition)
        if config.AdvancedMovieSelection.showcolorstatusinmovielist.value:
            self.list.append(self.Color1)
            self.list.append(self.Color2)
            self.list.append(self.Color3)
        self.list.append(self.Dateformat)
        if GP3Present and config.AdvancedMovieSelection.showfoldersinmovielist.value:
            self.list.append(self.Shownew)
        self.list.append(self.MiniTV)
        self.list.append(self.Jump2Mark)
        self["config"].list = self.list
        self["config"].l.setList(self.list)
        if not self.selectionChanged in self["config"].onSelectionChanged:
            self["config"].onSelectionChanged.append(self.selectionChanged)

    def selectionChanged(self):
        current = self["config"].getCurrent()
        if current == self.OnOff:
            self["help"].setText(_("Switch on/off the Advanced Movie Selection."))
        elif current == self.Startwith:
            self["help"].setText(_("Select Start button for the Advanced Movie Selection."))
        elif current == self.StartDir:
            self["help"].setText(_("Opens the film list on the last used location."))
        elif current == self.StartFirst:
            self["help"].setText(_("Always show selection in the first position in the movie list."))
        elif current == self.ShowMenu:
            self["help"].setText(_("Displays the Settings option in the menu at the movie list."))
        elif current == self.ShowColorkeys:
            self["help"].setText(_("Displays color key setup option in the menu at the movie list."))
        elif current == self.ShowSetup:
            self["help"].setText(_("Displays E2 movie list extensions in the menu at the movie list."))
        elif current == self.Showextras:
            self["help"].setText(_("Displays the various list view options in the menu at the movie list (Progressbar,View folders...)."))
        elif current == self.ShowSort:
            self["help"].setText(_("Displays sorting function in the menu at the movie list."))
        elif current == self.ShowListstyle:
            self["help"].setText(_("Displays various lists typs in the menu at the movie list (Minimal,Compact...)."))
        elif current == self.ShowMark:
            self["help"].setText(_("Displays mark movie as seen/unseen in the menu at the movie list."))
        elif current == self.ShowDel:
            self["help"].setText(_("Displays the movie delete function in the menu at the movie list."))
        elif current == self.ShowMove:
            self["help"].setText(_("Displays the movie move/copy function in the menu at the movie list."))
        elif current == self.ShowSearch:
            self["help"].setText(_("Displays the movie search function in the menu at the movie list."))
        elif current == self.ShowPreview:
            self["help"].setText(_("Displays the cover in the movie list."))            
        elif current == self.Coversize:
            self["help"].setText(_("Here you can determine the coverfile size for the download/save."))
        elif current == self.ShowCoverOptions:
            self["help"].setText(_("Displays movie info/cover options in the menu at the movie list."))
        elif current == self.ShowDelInfoCover:
            self["help"].setText(_("Displays delete movie info and cover function in the menu at the movie list."))
        elif current == self.ShowDelCover:
            self["help"].setText(_("Displays delete cover function in the menu at the movie list."))            
        elif current == self.ShowDelInfo:
            self["help"].setText(_("Displays delete movie info function in the menu at the movie list."))                 
        elif current == self.ShowRename:
            self["help"].setText(_("Displays rename function in the menu at the movie list."))
        elif current == self.ShowTMDb:
            self["help"].setText(_("Displays TMDb search in the menu at the movie list."))            
        elif current == self.MovieLength:
            self["help"].setText(_("This option is for many of the functions from the Advanced Movie Selection necessary. If this option is disabled are many functions not available."))
        elif current == self.Percentmark:
            self["help"].setText(_("With this option you can assign as when a film is marked as seen."))
        elif current == self.AskDelete:
            self["help"].setText(_("With this option you can turn on/off the security question before delete a movie."))
        elif current == self.Eventinfotyp:
            self["help"].setText(_("With this option you can assign what function should have the info button. The selection depends on the installed plugins."))
        elif current == self.Eventinfotyp2:
            self["help"].setText(_("With this option you can assign what function should have the info button. The selection depends on the installed plugins."))
        elif current == self.Eventinfotyp3:
            self["help"].setText(_("With this option you can assign what function should have the info button. The selection depends on the installed plugins."))
        elif current == self.Eventinfotyp4:
            self["help"].setText(_("With this option you can assign what function should have the info button. The selection depends on the installed plugins."))
        elif current == self.Eventinfotyp5:
            self["help"].setText(_("With this option you can assign what function should have the info button. The selection depends on the installed plugins."))
        elif current == self.Eventinfotyp6:
            self["help"].setText(_("With this option you can assign what function should have the info button. The selection depends on the installed plugins."))
        elif current == self.Eventinfotyp7:
            self["help"].setText(_("With this option you can assign what function should have the info button. The selection depends on the installed plugins."))
        elif current == self.MovieStart:
            self["help"].setText(_("With this option you can assign what should happen when a movie start."))
        elif current == self.MovieStop:
            self["help"].setText(_("With this option you can assign what should happen when a movie stop."))
        elif current == self.MovieEnd:
            self["help"].setText(_("With this option you can assign what should happen when the end of the films was achieved."))
        elif current == self.ShowMoviebarPosition:
            self["help"].setText(_("Displays the moviebar position setup function in the menu at the movie list."))
        elif current == self.Color1:
            self["help"].setText(_("With this option you can assign what color should displayed for not ready seen movies in movie list."))
        elif current == self.Color2:
            self["help"].setText(_("With this option you can assign what color should displayed for ready seen movies in movie list."))
        elif current == self.Color3:
            self["help"].setText(_("With this option you can assign what color should displayed for recording movies in movie list."))
        elif current == self.Dateformat:
            self["help"].setText(_("With this option you can assign the date format in movie list (7 different sizes are available)."))
        elif current == self.Shownew:
            self["help"].setText(_("With this option you can display a icon for new recordings."))
        elif current == self.MiniTV:
            self["help"].setText(_("With this option you can switch on/off the Mini TV in the movie list."))
        elif current == self.UseFolderName:
            self["help"].setText(_("With this option you can use the foldername instead of folder.jpg to display covers in folders."))
        elif current == self.ShowMovieTagsinMenu:
            self["help"].setText(_("Displays movie tags function in the menu at the movie list."))
        elif current == self.Jump2Mark:
            self["help"].setText(_("If this option is activated automatically when a movie does not start from the last position, the movie starts at the first marker."))
        elif current == self.ShowFilterbyTags:
            self["help"].setText(_("Displays filter by tags function in the menu at the movie list."))
        elif current == self.ShowTrailer:
            self["help"].setText(_("Displays search trailer on web function in the menu at the movie list."))

    def pluginsavailable(self):
        if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/IMDb/plugin.pyo"):
            self["IMDbtxt"].setText(_("IMDb plugin installed. Assign function to info button is possible."))
        else:
            self["IMDbtxt"].setText(_("IMDb plugin NOT installed. Assign function to info button is NOT possible."))
        if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/OFDb/plugin.pyo"):
            self["OFDbtxt"].setText(_("OFDb plugin installed. Assign function to info button is possible."))
        else:
            self["OFDbtxt"].setText(_("OFDb plugin NOT installed. Assign function to info button is NOT possible."))
        if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/TMDb/plugin.pyo"):
            self["TMDbtxt"].setText(_("TMDb plugin installed. Assign function to info button is possible."))
        else:
            self["TMDbtxt"].setText(_("TMDb plugin NOT installed. Assign function to info button is NOT possible.")) 
        if  YTTrailerPresent == True:
             self["Trailertxt"].setText(_("YTTrailer plugin installed. Search for trailers on the Web is possible."))
        else:
            self["Trailertxt"].setText(_("YTTrailer plugin NOT installed. Search for trailers on the Web is NOT possible."))           


    def cancelConfirm(self, result):
        if not result:
            return
        for x in self["config"].list:
            x[1].cancel()
        self.close()

    def keyCancel(self):
        if self["config"].isChanged():
            self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"))
        else:
            self.close()

    def keySave(self):
        if self.needsRestartFlag == True:
            self.session.openWithCallback(self.exitAnswer, MessageBoxEx, _("Some settings changes require a restart to take effect.\nIf you  use a skin without PiG (Picture in Graphic) you have to restart the box (not only Enigma 2)!\nWith YES only Enigma 2 starts new, with NO the box make a restart."), type=MessageBox.TYPE_YESNO)
        else:
            if self.needsReopenFlag == True:
                self.session.openWithCallback(self.save, MessageBox, _("Some settings changes require close/reopen the movielist to take effect."), type=MessageBox.TYPE_INFO)
            else:
                self.save()

    def exitAnswer(self, result):
        if result is None:
            self.session.open(MessageBox, _("Aborted by user !!"), MessageBox.TYPE_ERROR)
        if result is False:
            self.save()
            quitMainloop(2)
        if result:
            self.save()
            quitMainloop(3)

    def save(self, retval=None):
        ConfigListScreen.keySave(self)
            
    def about(self):
        self.session.open(AdvancedMovieSelectionAbout)
        
    def buttonsetup(self):
        self.session.open(AdvancedMovieSelectionButtonSetup)
            
    def RecPathSettings(self):
        self.session.open(RecordPathsSettings)
        
class AdvancedMovieSelectionButtonSetup(Screen, ConfigListScreen):
    def __init__(self, session, args=None):
        Screen.__init__(self, session)
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            self.skinName = ["AdvancedMovieSelectionButtonSetupHD"]
        elif sz_w == 1024:
            self.skinName = ["AdvancedMovieSelectionButtonSetupXD"]
        else:
            self.skinName = ["AdvancedMovieSelectionButtonSetupSD"]
        self["important"] = StaticText(_("IMPORTANT: If changes are made here the Advanced Movie Selection must be completely closed so the changes can be adopted !!"))
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Save/Close"))
        self["key_yellow"] = Button(_("Own button description"))
        self["OKIcon"] = Pixmap()
        self["OKIcon"].hide()
        self.entryguilist = []
        self.entryguilist.append(("0", _("Nothing")))
        self.entryguilist.append(("1", _("Delete")))
        self.entryguilist.append(("2", _("Home")))
        self.entryguilist.append(("3", _("Sort")))
        self.entryguilist.append(("4", _("Bookmark 1")))
        self.entryguilist.append(("5", _("Bookmark 2")))
        self.entryguilist.append(("6", _("Bookmark 3")))
        self.entryguilist.append(("7", _("Filter by Tags")))
        self.entryguilist.append(("8", _("Move-Copy")))
        if YTTrailerPresent == True:
            self.entryguilist.append(("9", _("Trailer search")))
            index = 10
        else:
            index = 9
        self.entryguilist2 = []
        self.entryguilist2.append(("0", _("Nothing")))
        self.entryguilist2.append(("1", _("DM-600PVR")))
        self.entryguilist2.append(("2", _("DM-7000")))
        self.entryguilist2.append(("3", _("DM-7025")))
        self.entryguilist2.append(("4", _("DM-8000HD")))
        self.entryguilist2.append(("5", _("DM-500HD")))
        self.entryguilist2.append(("6", _("DM-800HD")))
        self.entryguilist2.append(("7", _("DM-800HDse")))
        self.entryguilist2.append(("8", _("DM-7020HD")))
        self.entryguilist2.append(("9", _("internal HDD")))
        self.entryguilist2.append(("10", _("NAS")))
        self.entryguilist2.append(("11", _("NAS-Movies")))
        self.entryguilist2.append(("12", (config.AdvancedMovieSelection.homeowntext.value)))
        self.entryguilist2.append(("13", (config.AdvancedMovieSelection.bookmark1owntext.value)))
        self.entryguilist2.append(("14", (config.AdvancedMovieSelection.bookmark2owntext.value)))
        self.entryguilist2.append(("15", (config.AdvancedMovieSelection.bookmark3owntext.value)))
        self.entryguilist3 = []
        self.entryguilist3.append(("0", _("Display plugin name")))
        self.entryguilist3.append(("1", _("Display plugin description")))        

        red_selectedindex = self.getStaticName(config.AdvancedMovieSelection.red.value)
        green_selectedindex = self.getStaticName(config.AdvancedMovieSelection.green.value)
        yellow_selectedindex = self.getStaticName(config.AdvancedMovieSelection.yellow.value)
        blue_selectedindex = self.getStaticName(config.AdvancedMovieSelection.blue.value)
        buttoncaptionchoice_selectedindex = self.getStaticName3(config.AdvancedMovieSelection.buttoncaption.value)
        hometext_selectedindex = self.getStaticName2(config.AdvancedMovieSelection.hometext.value)
        bookmark1buttontext_selectedindex = self.getStaticName2(config.AdvancedMovieSelection.bookmark1text.value)
        bookmark2buttontext_selectedindex = self.getStaticName2(config.AdvancedMovieSelection.bookmark2text.value)
        bookmark3buttontext_selectedindex = self.getStaticName2(config.AdvancedMovieSelection.bookmark3text.value)
        
        for p in plugins.getPlugins(where=[PluginDescriptor.WHERE_MOVIELIST]):
            self.entryguilist.append((str(index), str(p.name)))
            if config.AdvancedMovieSelection.red.value == str(p.name):
                red_selectedindex = str(index)
            if config.AdvancedMovieSelection.green.value == str(p.name):
                green_selectedindex = str(index)
            if config.AdvancedMovieSelection.yellow.value == str(p.name):
                yellow_selectedindex = str(index)
            if config.AdvancedMovieSelection.blue.value == str(p.name):
                blue_selectedindex = str(index)
            index = index + 1
        
        self.redchoice = ConfigSelection(default=red_selectedindex, choices=self.entryguilist)
        self.greenchoice = ConfigSelection(default=green_selectedindex, choices=self.entryguilist)
        self.yellowchoice = ConfigSelection(default=yellow_selectedindex, choices=self.entryguilist)
        self.bluechoice = ConfigSelection(default=blue_selectedindex, choices=self.entryguilist)
        self.buttoncaptionchoice = ConfigSelection(default=buttoncaptionchoice_selectedindex, choices=self.entryguilist3)
        self.homebuttontextchoice = ConfigSelection(default=hometext_selectedindex, choices=self.entryguilist2)
        self.bookmark1buttontextchoice = ConfigSelection(default=bookmark1buttontext_selectedindex, choices=self.entryguilist2)
        self.bookmark2buttontextchoice = ConfigSelection(default=bookmark2buttontext_selectedindex, choices=self.entryguilist2)
        self.bookmark3buttontextchoice = ConfigSelection(default=bookmark3buttontext_selectedindex, choices=self.entryguilist2)
        
        ConfigListScreen.__init__(self, [])
        self.initConfigList()
        
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
        {
            "green": self.keySave,
            "yellow": self.ownname,
            "cancel": self.cancel,
            "ok": self.ok,
        }, -2)
        self.onLayoutFinish.append(self.setCustomTitle)
        
    def setCustomTitle(self):
        self.setTitle(_("Movie Quick Button Setup"))

    def initConfigList(self):
        hometmp = config.movielist.videodirs.value
        homedefault = config.AdvancedMovieSelection.homepath.value
        if homedefault not in hometmp:
            hometmp = hometmp[:]
            hometmp.append(homedefault)
        self.homepath_dirname = ConfigSelection(default=homedefault, choices=hometmp)
        hometmp = config.movielist.videodirs.value
        homedefault = config.AdvancedMovieSelection.homepath.value

        book1tmp = config.movielist.videodirs.value
        book1default = config.AdvancedMovieSelection.bookmark1path.value
        if book1default not in book1tmp:
            book1tmp = book1tmp[:]
            book1tmp.append(book1default)
        self.bookmark1_dirname = ConfigSelection(default=book1default, choices=book1tmp)
        book1tmp = config.movielist.videodirs.value
        book1default = config.AdvancedMovieSelection.bookmark1path.value

        book2tmp = config.movielist.videodirs.value
        book2default = config.AdvancedMovieSelection.bookmark2path.value
        if book2default not in book2tmp:
            book2tmp = book2tmp[:]
            book2tmp.append(book2default)
        self.bookmark2_dirname = ConfigSelection(default=book2default, choices=book2tmp)
        book2tmp = config.movielist.videodirs.value
        book2default = config.AdvancedMovieSelection.bookmark2path.value

        book3tmp = config.movielist.videodirs.value
        book3default = config.AdvancedMovieSelection.bookmark3path.value
        if book3default not in book3tmp:
            book3tmp = book3tmp[:]
            book3tmp.append(book3default)
        self.bookmark3_dirname = ConfigSelection(default=book3default, choices=book3tmp)
        book3tmp = config.movielist.videodirs.value
        book3default = config.AdvancedMovieSelection.bookmark3path.value

        self.list = []
        self.redkey = getConfigListEntry(_("Assigned to red key"), self.redchoice)
        self.list.append(self.redkey)
        self.greenkey = getConfigListEntry(_("Assigned to green key"), self.greenchoice)
        self.list.append(self.greenkey)
        self.yellowkey = getConfigListEntry(_("Assigned to yellow key"), self.yellowchoice)
        self.list.append(self.yellowkey)
        self.bluekey = getConfigListEntry(_("Assigned to blue key"), self.bluechoice)
        self.list.append(self.bluekey)
        self.button_caption = getConfigListEntry(_("Button caption"), self.buttoncaptionchoice)
        self.list.append(self.button_caption)
        self.home_button_text = getConfigListEntry(_("Home button text"), self.homebuttontextchoice)
        self.list.append(self.home_button_text)
        self.bookmark_1_button_text = getConfigListEntry(_("Bookmark 1 button text"), self.bookmark1buttontextchoice)
        self.list.append(self.bookmark_1_button_text)
        self.bookmark_2_button_text = getConfigListEntry(_("Bookmark 2 button text"), self.bookmark2buttontextchoice)
        self.list.append(self.bookmark_2_button_text)
        self.bookmark_3_button_text = getConfigListEntry(_("Bookmark 3 button text"), self.bookmark3buttontextchoice)
        self.list.append(self.bookmark_3_button_text)
        self.homepath = getConfigListEntry(_("Home path"), self.homepath_dirname)
        self.list.append(self.homepath)
        self.bookmark1 = getConfigListEntry(_("Bookmark 1 path"), self.bookmark1_dirname)
        self.list.append(self.bookmark1)
        self.bookmark2 = getConfigListEntry(_("Bookmark 2 path"), self.bookmark2_dirname)
        self.list.append(self.bookmark2)
        self.bookmark3 = getConfigListEntry(_("Bookmark 3 path"), self.bookmark3_dirname)
        self.list.append(self.bookmark3)
        self["config"].setList(self.list)
        if not self.selectionChanged in self["config"].onSelectionChanged:
            self["config"].onSelectionChanged.append(self.selectionChanged)
            
    def selectionChanged(self):
        current = self["config"].getCurrent()
        if current == self.bookmark_3_button_text:
            self.disableOKIcon()
        elif current == self.homepath:
            self.enableOKIcon()
        elif current == self.bookmark1:
            self.enableOKIcon()
        elif current == self.bookmark2:
            self.enableOKIcon()
        elif current == self.bookmark3:
            self.enableOKIcon()
        elif current == self.redkey:
            self.disableOKIcon()

    def enableOKIcon(self):
        self["OKIcon"].show()

    def disableOKIcon(self):
        self["OKIcon"].hide()

    def ok(self):
        currentry = self["config"].getCurrent()
        self.lastvideodirs = config.movielist.videodirs.value
        if currentry == self.homepath:
            self.entrydirname = self.homepath_dirname
            self.session.openWithCallback(self.dirnameSelected, MovieLocationBox, _("Movie Quick Button Home path"), preferredPath(self.homepath_dirname.value))
        elif currentry == self.bookmark1:
            self.entrydirname = self.bookmark1_dirname
            self.session.openWithCallback(self.dirnameSelected, MovieLocationBox, _("Movie Quick Button Bookmark 1 path"), preferredPath(self.bookmark1_dirname.value))
        elif currentry == self.bookmark2:
            self.entrydirname = self.bookmark2_dirname 
            self.session.openWithCallback(self.dirnameSelected, MovieLocationBox, _("Movie Quick Button Bookmark 2 path"), preferredPath(self.bookmark2_dirname.value))     
        elif currentry == self.bookmark3:
            self.entrydirname = self.bookmark3_dirname
            self.session.openWithCallback(self.dirnameSelected, MovieLocationBox, _("Movie Quick Button Bookmark 3 path"), preferredPath(self.bookmark3_dirname.value))                 

    def dirnameSelected(self, res):
        if res is not None:
            self.entrydirname.value = res
            if config.movielist.videodirs.value != self.lastvideodirs:
                tmp = config.movielist.videodirs.value
                default = self.homepath_dirname.value
                if default not in tmp:
                    tmp = tmp[:]
                    tmp.append(default)
                self.homepath_dirname.setChoices(tmp, default=default)
                tmp = config.movielist.videodirs.value
            if config.movielist.videodirs.value != self.lastvideodirs:
                default = self.bookmark1_dirname.value
                if default not in tmp:
                    tmp = tmp[:]
                    tmp.append(default)
                self.bookmark1_dirname.setChoices(tmp, default=default)
                tmp = config.movielist.videodirs.value
            if config.movielist.videodirs.value != self.lastvideodirs:
                default = self.bookmark2_dirname.value
                if default not in tmp:
                    tmp = tmp[:]
                    tmp.append(default)
                self.bookmark2_dirname.setChoices(tmp, default=default)
                tmp = config.movielist.videodirs.value
            if config.movielist.videodirs.value != self.lastvideodirs:                   
                default = self.bookmark3_dirname.value
                if default not in tmp:
                    tmp = tmp[:]
                    tmp.append(default)
                self.bookmark3_dirname.setChoices(tmp, default=default)
                tmp = config.movielist.videodirs.value
                
    def keySave(self):
        self["config"].getCurrent()
        #currentry = self["config"].getCurrent()
        config.AdvancedMovieSelection.buttoncaption.value = self.entryguilist3[int(self.buttoncaptionchoice.value)][1]
        config.AdvancedMovieSelection.homepath.value = self.homepath_dirname.value
        config.AdvancedMovieSelection.bookmark1path.value = self.bookmark1_dirname.value
        config.AdvancedMovieSelection.bookmark2path.value = self.bookmark2_dirname.value
        config.AdvancedMovieSelection.bookmark3path.value = self.bookmark3_dirname.value            
        config.AdvancedMovieSelection.red.value = self.entryguilist[int(self.redchoice.value)][1]
        config.AdvancedMovieSelection.green.value = self.entryguilist[int(self.greenchoice.value)][1]
        config.AdvancedMovieSelection.yellow.value = self.entryguilist[int(self.yellowchoice.value)][1]
        config.AdvancedMovieSelection.blue.value = self.entryguilist[int(self.bluechoice.value)][1]
        config.AdvancedMovieSelection.hometext.value = self.entryguilist2[int(self.homebuttontextchoice.value)][1]
        config.AdvancedMovieSelection.bookmark1text.value = self.entryguilist2[int(self.bookmark1buttontextchoice.value)][1]
        config.AdvancedMovieSelection.bookmark2text.value = self.entryguilist2[int(self.bookmark2buttontextchoice.value)][1]
        config.AdvancedMovieSelection.bookmark3text.value = self.entryguilist2[int(self.bookmark3buttontextchoice.value)][1]
        config.AdvancedMovieSelection.buttoncaption.save()
        config.AdvancedMovieSelection.homepath.save()
        config.AdvancedMovieSelection.bookmark1path.save()
        config.AdvancedMovieSelection.bookmark2path.save()
        config.AdvancedMovieSelection.bookmark3path.save()
        config.AdvancedMovieSelection.red.save()
        config.AdvancedMovieSelection.green.save()
        config.AdvancedMovieSelection.yellow.save()
        config.AdvancedMovieSelection.blue.save()
        config.AdvancedMovieSelection.hometext.save()
        config.AdvancedMovieSelection.bookmark1text.save()
        config.AdvancedMovieSelection.bookmark2text.save()
        config.AdvancedMovieSelection.bookmark3text.save()
        config.AdvancedMovieSelection.save()
        configfile.save()
        self.close()

    def getStaticName(self, value):
        if value == _("Delete"):
            return "1"
        elif value == _("Home"):
            return "2"
        elif value == _("Sort"):
            return "3"
        elif value == _("Bookmark 1"):
            return "4"
        elif value == _("Bookmark 2"):
            return "5"
        elif value == _("Bookmark 3"):
            return "6"
        elif value == _("Filter by Tags"):
            return "7"
        elif value == _("Trailer search"):
            return "8"
        elif value == _("Move-Copy"):
            return "9"
        else:
            return "0"

    def getStaticName2(self, value):
        if value == _("DM-600PVR"):
            return "1"
        elif value == _("DM-7000"):
            return "2"
        elif value == _("DM-7025"):
            return "3"
        elif value == _("DM-8000HD"):
            return "4"
        elif value == _("DM-500HD"):
            return "5"
        elif value == _("DM-800HD"):
            return "6"
        elif value == _("DM-800HDse"):
            return "7"
        elif value == _("DM-7020HD"):
            return "8"
        elif value == _("internal HDD"):
            return "9"
        elif value == _("NAS"):
            return "10"
        elif value == _("NAS-Movies"):
            return "11"
        elif value == (config.AdvancedMovieSelection.homeowntext.value):
            return "12"
        elif value == (config.AdvancedMovieSelection.bookmark1owntext.value):
            return "13"
        elif value == (config.AdvancedMovieSelection.bookmark2owntext.value):
            return "14"
        elif value == (config.AdvancedMovieSelection.bookmark3owntext.value):
            return "15"
        else:
            return "0"

    def getStaticName3(self, value):
        if value == _("Display plugin name"):
            return "0"
        elif value == _("Display plugin description"):
            return "1"
        else:
            return "0"

    def cancel(self):
        self.close()

    def ownname(self):
        self.session.openWithCallback(self.cancel, AdvancedMovieSelectionOwnButtonName)

class AdvancedMovieSelectionOwnButtonName(Screen, ConfigListScreen):        
    def __init__(self, session):
        Screen.__init__(self, session)
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            self.skinName = ["AdvancedMovieSelectionOwnButtonNameHD"]
        elif sz_w == 1024:
            self.skinName = ["AdvancedMovieSelectionOwnButtonNameXD"]
        else:
            self.skinName = ["AdvancedMovieSelectionOwnButtonNameSD"]
        self.session = session
        self.homebutton = None
        self.bookmark1button = None
        self.bookmark2button = None
        self.bookmark3button = None
        self["setupActions"] = ActionMap(["ColorActions", "OkCancelActions"],
        {
            "red": self.keySave,
            "cancel": self.keyCancel
        }, -2) 
        self["VirtualKB"] = ActionMap(["VirtualKeyboardActions" ],
        {
            "showVirtualKeyboard": self.KeyText,
        }, -1)
        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session)
        self["menu"] = List(self.list)
        self["help"] = StaticText()
        self["key_red"] = StaticText(_("Save/Close"))
        self["VKeyIcon"] = Pixmap()
        self["HelpWindow"] = Pixmap()
        self["VKeyIcon"].hide()
        self["VirtualKB"].setEnabled(False)
        self.onShown.append(self.setWindowTitle)
        self.createSetup()

    def setWindowTitle(self, retval=None):
        self.setTitle(_("Movie Quick Button Name Setup"))

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.createSetup()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.createSetup()

    def KeyText(self):
        if self["config"].getCurrent() == self.homebutton:
            self.session.openWithCallback(self.homebuttonCallback, VirtualKeyBoard, title=(_("Enter Home button descrition:")), text=config.AdvancedMovieSelection.homeowntext.value)
        if self["config"].getCurrent() == self.bookmark1button:
            self.session.openWithCallback(self.bookmark1buttonCallback, VirtualKeyBoard, title=(_("Enter Bookmark 1 button descrition:")), text=config.AdvancedMovieSelection.bookmark1owntext.value)
        if self["config"].getCurrent() == self.bookmark2button:
            self.session.openWithCallback(self.bookmark2buttonCallback, VirtualKeyBoard, title=(_("Enter Bookmark 2 button descrition:")), text=config.AdvancedMovieSelection.bookmark2owntext.value)
        if self["config"].getCurrent() == self.bookmark3button:
            self.session.openWithCallback(self.bookmark3buttonCallback, VirtualKeyBoard, title=(_("Enter Bookmark 3 button descrition:")), text=config.AdvancedMovieSelection.bookmark3owntext.value)

    def homebuttonCallback(self, callback=None):
        if callback is not None and len(callback):
            config.AdvancedMovieSelection.homeowntext.setValue(callback)
            self["config"].invalidate(self.homebutton)

    def bookmark1buttonCallback(self, callback=None):
        if callback is not None and len(callback):
            config.AdvancedMovieSelection.bookmark1owntext.setValue(callback)
            self["config"].invalidate(self.bookmark1button)

    def bookmark2buttonCallback(self, callback=None):
        if callback is not None and len(callback):
            config.AdvancedMovieSelection.bookmark2owntext.setValue(callback)
            self["config"].invalidate(self.bookmark2button)

    def bookmark3buttonCallback(self, callback=None):
        if callback is not None and len(callback):
            config.AdvancedMovieSelection.bookmark3owntext.setValue(callback)
            self["config"].invalidate(self.bookmark3button)
        
    def createSetup(self, retval=None):
        self.list = []
        self.homebutton = getConfigListEntry(_("Home button description:"), config.AdvancedMovieSelection.homeowntext)
        self.bookmark1button = getConfigListEntry(_("Bookmark 1 button description:"), config.AdvancedMovieSelection.bookmark1owntext)
        self.bookmark2button = getConfigListEntry(_("Bookmark 2 button description:"), config.AdvancedMovieSelection.bookmark2owntext)
        self.bookmark3button = getConfigListEntry(_("Bookmark 3 button description:"), config.AdvancedMovieSelection.bookmark3owntext)
        self.list.append(self.homebutton)
        self.list.append(self.bookmark1button)
        self.list.append(self.bookmark2button)
        self.list.append(self.bookmark3button)
        self["config"].list = self.list
        self["config"].l.setList(self.list)
        if not self.selectionChanged in self["config"].onSelectionChanged:
            self["config"].onSelectionChanged.append(self.selectionChanged)

    def selectionChanged(self):
        current = self["config"].getCurrent()
        if current == self.homebutton:
            self["help"].setText(_("Here you can give the home button a special name. After saving the changes color key settings will be closed, reopen it then the changes is to selection."))
            self.enableVKeyIcon()
            self.showKeypad()
        elif current == self.bookmark1button:
            self["help"].setText(_("Here you can give the bookmark 1 button a special name. After saving the changes color key settings will be closed, reopen it then the changes is to selection."))
            self.enableVKeyIcon()
            self.showKeypad()
        elif current == self.bookmark2button:
            self["help"].setText(_("Here you can give the bookmark 2 button a special name. After saving the changes color key settings will be closed, reopen it then the changes is to selection."))
            self.enableVKeyIcon()
            self.showKeypad()
        elif current == self.bookmark3button:
            self["help"].setText(_("Here you can give the bookmark 3 button a special name. After saving the changes color key settings will be closed, reopen it then the changes is to selection."))
            self.enableVKeyIcon()
            self.showKeypad()

    def enableVKeyIcon(self):
        self["VKeyIcon"].show()
        self["VirtualKB"].setEnabled(True)

    def disableVKeyIcon(self):
        self["VKeyIcon"].hide()
        self["VirtualKB"].setEnabled(False)

    def showKeypad(self, retval=None):
        current = self["config"].getCurrent()
        helpwindowpos = self["HelpWindow"].getPosition()
        if hasattr(current[1], 'help_window'):
            if current[1].help_window.instance is not None:
                current[1].help_window.instance.show()
                current[1].help_window.instance.move(ePoint(helpwindowpos[0], helpwindowpos[1]))

    def hideKeypad(self):
        current = self["config"].getCurrent()
        if hasattr(current[1], 'help_window'):
            if current[1].help_window.instance is not None:
                current[1].help_window.instance.hide()

    def cancelConfirm(self, result):
        if not result:
            self.showKeypad()
            return
        for x in self["config"].list:
            x[1].cancel()
        self.close()

    def keyCancel(self):
        print "cancel"
        if self["config"].isChanged():
            self.hideKeypad()
            self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings ?"))
        else:
            self.close()

    def keySave(self):
        print "saving"
        ConfigListScreen.keySave(self)
