#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  The plugin is developed on the basis from a lot of single plugins (thx for the code @ all)
#  Coded by JackDaniel & cmikula (c)2011
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
from Components.PluginComponent import plugins
from Screens.Screen import Screen
from Components.ActionMap import HelpableActionMap, ActionMap, NumberActionMap
from Components.MenuList import MenuList
from Components.Sources.StaticText import StaticText
from Screens.HelpMenu import HelpableScreen
from MovieList import MovieList, eServiceReferenceHotplug, eServiceReferenceBackDir, eServiceReferenceVDir
from MovieSearch import MovieSearchScreen
from Components.DiskInfo import DiskInfo
from Components.Pixmap import Pixmap
from Components.Label import Label
from Components.config import config, ConfigSubsection, ConfigText, ConfigInteger, ConfigLocations, ConfigSet
from Components.UsageConfig import defaultMoviePath
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.LocationBox import MovieLocationBox
from AdvancedMovieSelectionSetup import AdvancedMovieSelectionSetup, AdvancedMovieSelectionButtonSetup
from Tools.BoundFunction import boundFunction
from Tools.Directories import resolveFilename, fileExists, SCOPE_HDD, SCOPE_CURRENT_SKIN
from enigma import eServiceReference, eServiceCenter, eSize, ePoint, eTimer, getDesktop, iServiceInformation
from Screens.Console import eConsoleAppContainer
from ServiceProvider import ServiceEvent
from MoveCopy import MovieMove
from Rename import MovieRetitle
from SearchTMDb import TMDbMain as TMDbMainsave
from MoviePreview import MoviePreview
from DownloadMovies import DownloadMovies
from ServiceProvider import eServiceReferenceDvd
from TagEditor import MovieTagEditor
from QuickButton import QuickButton
from os import path
import os
import NavigationInstance
from timer import TimerEntry
from Trashcan import Trashcan
from RecordTimer import AFTEREVENT
#from MessageBoxEx import MessageBox as MessageBoxEx
from time import localtime, strftime
from datetime import datetime
from Tools.FuzzyDate import FuzzyTime

if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/IMDb/plugin.pyo"):
    from Plugins.Extensions.IMDb.plugin import IMDB
    IMDbPresent = True
else:
    IMDbPresent = False
if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/OFDb/plugin.pyo"):
    from Plugins.Extensions.OFDb.plugin import OFDB
    OFDbPresent = True
else:
    OFDbPresent = False
if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/TMDb/plugin.pyo"):
    from Plugins.Extensions.TMDb.plugin import TMDbMain
    TMDbPresent = True
else:
    TMDbPresent = False
if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/YTTrailer/plugin.pyo"):
    from Plugins.Extensions.YTTrailer.plugin import YTTrailerList
    YTTrailerPresent = True
else:
    YTTrailerPresent = False
if fileExists("/usr/lib/enigma2/python/Plugins/Bp/geminimain/plugin.pyo"):
    GP3Present = True
else:
    GP3Present = False

config.movielist = ConfigSubsection()
config.movielist.moviesort = ConfigInteger(default=MovieList.SORT_ALPHANUMERIC)
config.movielist.listtype = ConfigInteger(default=MovieList.LISTTYPE_ORIGINAL)
config.movielist.description = ConfigInteger(default=MovieList.HIDE_DESCRIPTION)
config.movielist.last_videodir = ConfigText(default=resolveFilename(SCOPE_HDD))
config.movielist.last_timer_videodir = ConfigText(default=resolveFilename(SCOPE_HDD))
config.movielist.videodirs = ConfigLocations(default=[resolveFilename(SCOPE_HDD)])
config.movielist.first_tags = ConfigText(default="")
config.movielist.second_tags = ConfigText(default="")
config.movielist.last_selected_tags = ConfigSet([], default=[])
config.movielist.showtime = ConfigInteger(default=MovieList.SHOW_TIME)
config.movielist.showdate = ConfigInteger(default=MovieList.SHOW_DATE)
config.movielist.showservice = ConfigInteger(default=MovieList.SHOW_SERVICE)
config.movielist.showtags = ConfigInteger(default=MovieList.HIDE_TAGS)

SHOW_ALL_MOVIES = _("Show all movies")

def getDateString():
    t = localtime()
    if t.tm_wday == 0:
        wday = "Montag"
    elif t.tm_wday == 1:
        wday = "Dienstag"
    elif t.tm_wday == 2:
        wday = "Mittwoch"
    elif t.tm_wday == 3:
        wday = "Donnerstag"
    elif t.tm_wday == 4:
        wday = "Freitag"
    elif t.tm_wday == 5:
        wday = "Samstag"
    elif t.tm_wday == 6:
        wday = "Sonntag"
    else:
        wday = ""
    if config.osd.language.value == "de_DE":
        desc = (("%s.%s.%s\n%s") % (t.tm_mday, t.tm_mon, t.tm_year, wday))
    else:
        desc = strftime("%d.%m.%Y\n%A", t)
    return desc

def getBeginTimeString(info, serviceref):
    if not info or not serviceref:
        return ""
    begin = info.getInfo(serviceref, iServiceInformation.sTimeCreate)
    if not begin: 
        return ""
    if config.AdvancedMovieSelection.dateformat.value == "2":
        ft = FuzzyTime(begin)
        desc = ft[0] + ", " + ft[1]
    else:
        d = datetime.fromtimestamp(begin)
        desc = d.strftime("%d.%m.%Y - %H:%M")
    return desc

class MovieContextMenu(Screen):
    def __init__(self, session, csel, service):
        Screen.__init__(self, session)
        self.csel = csel
        self.service = service
        self["actions"] = ActionMap(["OkCancelActions"],
            {
                "ok": self.okbuttonClick,
                "cancel": self.cancelClick
            })
        menu = []
        if config.AdvancedMovieSelection.hotplug.value and isinstance(service, eServiceReferenceHotplug):
            menu.append((_("Unmount") + " " + service.getName(), boundFunction(self.unmount)))
        if config.AdvancedMovieSelection.showtmdb.value:
            if not (self.service.flags & eServiceReference.mustDescent):
                menu.append((_("TMDb search"), boundFunction(self.imdbsearch)))
        if config.AdvancedMovieSelection.showdelete.value:
            if not (self.service.flags & eServiceReference.mustDescent):
                menu.append((_("Delete"), self.delete))
        if config.AdvancedMovieSelection.use_wastebasket.value and config.AdvancedMovieSelection.show_wastebasket.value:
            menu.append((_("Wastebasket"), self.waste))
        if config.AdvancedMovieSelection.showmove.value and not (self.service.flags & eServiceReference.mustDescent):
            menu.append((_("Move/Copy"), self.movecopy))
        if not (isinstance(service, eServiceReferenceBackDir) or isinstance(service, eServiceReferenceVDir) or isinstance(service, eServiceReferenceHotplug)):
            if config.AdvancedMovieSelection.showrename.value:
                menu.append((_("Rename"), boundFunction(self.retitel, session, service)))
        if config.AdvancedMovieSelection.showsearch.value:
            menu.append((_("Movie search"), boundFunction(self.searchmovie)))
        if config.AdvancedMovieSelection.showmark.value and config.usage.load_length_of_movies_in_moviellist.value and not (self.service.flags & eServiceReference.mustDescent):
            menu.append((_("Mark movie as seen"), boundFunction(self.setMovieStatus, 1)))
            menu.append((_("Mark movie as unseen"), boundFunction(self.setMovieStatus, 0)))
        if GP3Present and config.AdvancedMovieSelection.marknewicon.value and not (self.service.flags & eServiceReference.mustDescent):
            menu.append((_("Mark movie with new recordings icon"), boundFunction(self.marknewicon)))
        if config.AdvancedMovieSelection.pluginmenu_list.value:
            if not (self.service.flags & eServiceReference.mustDescent):
                menu.extend([(p.description, boundFunction(self.execPlugin, p)) for p in plugins.getPlugins(PluginDescriptor.WHERE_MOVIELIST)])
        if config.AdvancedMovieSelection.showsort.value:
            if config.movielist.moviesort.value == MovieList.SORT_ALPHANUMERIC:
                menu.append((_("Sort by date (descending)"), boundFunction(self.sortBy, MovieList.SORT_DATE_DESC)))
                menu.append((_("Sort by date (ascending)"), boundFunction(self.sortBy, MovieList.SORT_DATE_ASC)))
            else:
                menu.append((_("Alphabetic sort"), boundFunction(self.sortBy, MovieList.SORT_ALPHANUMERIC)))
                if config.movielist.moviesort.value == MovieList.SORT_DATE_DESC:
                    menu.append((_("Sort by date (ascending)"), boundFunction(self.sortBy, MovieList.SORT_DATE_ASC)))
                else:
                    menu.append((_("Sort by date (descending)"), boundFunction(self.sortBy, MovieList.SORT_DATE_DESC)))
        if config.AdvancedMovieSelection.showliststyle.value:
            menu.extend((
                (_("List style default"), boundFunction(self.listType, MovieList.LISTTYPE_ORIGINAL)),
                (_("List style compact with description"), boundFunction(self.listType, MovieList.LISTTYPE_COMPACT_DESCRIPTION)),
                (_("List style compact"), boundFunction(self.listType, MovieList.LISTTYPE_COMPACT)),
                (_("List style Advanced Movie Selection single line"), boundFunction(self.listType, MovieList.LISTTYPE_MINIMAL_AdvancedMovieSelection)),
                (_("List style single line"), boundFunction(self.listType, MovieList.LISTTYPE_MINIMAL))
            ))
        if config.AdvancedMovieSelection.showliststyle.value and config.movielist.listtype.value == MovieList.LISTTYPE_MINIMAL_AdvancedMovieSelection:
            if config.movielist.showservice.value == MovieList.SHOW_SERVICE:
                menu.append((_("Hide broadcaster"), boundFunction(self.showService, MovieList.HIDE_SERVICE)))
            else:
                menu.append((_("Show broadcaster"), boundFunction(self.showService, MovieList.SHOW_SERVICE)))
        if config.AdvancedMovieSelection.showliststyle.value and config.movielist.listtype.value == MovieList.LISTTYPE_MINIMAL_AdvancedMovieSelection or config.movielist.listtype.value == MovieList.LISTTYPE_ORIGINAL or config.movielist.listtype.value == MovieList.LISTTYPE_COMPACT and config.movielist.showservice.value == MovieList.HIDE_SERVICE:
            if config.movielist.showtags.value == MovieList.SHOW_TAGS:
                menu.append((_("Hide tags in movielist"), boundFunction(self.showTags, MovieList.HIDE_TAGS)))
            else:
                menu.append((_("Show tags in movielist"), boundFunction(self.showTags, MovieList.SHOW_TAGS)))
        if config.AdvancedMovieSelection.showliststyle.value:
            if config.movielist.description.value == MovieList.SHOW_DESCRIPTION:
                menu.append((_("Hide extended description"), boundFunction(self.showDescription, MovieList.HIDE_DESCRIPTION)))
            else:
                menu.append((_("Show extended description"), boundFunction(self.showDescription, MovieList.SHOW_DESCRIPTION)))
            if config.movielist.showdate.value == MovieList.SHOW_DATE:
                menu.append((_("Hide date entry in movielist"), boundFunction(self.showDate, MovieList.HIDE_DATE)))
            else:
                menu.append((_("Show date entry in movielist"), boundFunction(self.showDate, MovieList.SHOW_DATE)))
            if config.movielist.showtime.value == MovieList.SHOW_TIME:
                menu.append((_("Hide runtime entry in movielist"), boundFunction(self.showTime, MovieList.HIDE_TIME)))
            else:
                menu.append((_("Show runtime entry in movielist"), boundFunction(self.showTime, MovieList.SHOW_TIME)))
        if config.AdvancedMovieSelection.showextras.value:
            if config.AdvancedMovieSelection.showfoldersinmovielist.value:
                menu.append((_("Hide folders in movielist"), boundFunction(self.showFolders, False)))
            else:
                menu.append((_("Show folders in movielist"), boundFunction(self.showFolders, True)))
        if config.AdvancedMovieSelection.showextras.value and config.usage.load_length_of_movies_in_moviellist.value:
            if config.AdvancedMovieSelection.showprogessbarinmovielist.value:
                menu.append((_("Hide progressbar in movielist"), boundFunction(self.showProgressbar, False)))
            else:
                menu.append((_("Show progressbar in movielist"), boundFunction(self.showProgressbar, True)))
        if config.AdvancedMovieSelection.showextras.value and config.AdvancedMovieSelection.showfoldersinmovielist.value and config.usage.load_length_of_movies_in_moviellist.value:
            if config.AdvancedMovieSelection.showiconstatusinmovielist.value:
                menu.append((_("Hide movie status icon in movielist"), boundFunction(self.showStatusIcon, False)))
            else:
                menu.append((_("Show movie status icon in movielist"), boundFunction(self.showStatusIcon, True)))
        if config.AdvancedMovieSelection.showextras.value and config.usage.load_length_of_movies_in_moviellist.value:
            if config.AdvancedMovieSelection.showcolorstatusinmovielist.value:
                menu.append((_("Hide movie color status in movielist"), boundFunction(self.showStatusColor, False)))
            else:
                menu.append((_("Show movie color status in movielist"), boundFunction(self.showStatusColor, True)))
        if config.AdvancedMovieSelection.showcolorkey.value:        
            menu.append((_("Color key settings"), self.setupbutton))     
        if config.AdvancedMovieSelection.showpreview.value and config.AdvancedMovieSelection.showcoveroptions.value and config.AdvancedMovieSelection.showcoveroptions2.value:
            menu.append((_("Download and save movie info/cover for all movies"), boundFunction(self.downloadMovieInfoAll)))
        if config.AdvancedMovieSelection.showpreview.value and config.AdvancedMovieSelection.showcoveroptions.value:
            if not service.flags & eServiceReference.mustDescent:
                menu.append((_("Download and save movie info/cover"), self.downloadMovieInfo))              
        if config.AdvancedMovieSelection.showpreview.value and config.AdvancedMovieSelection.show_update_genre.value:
            menu.append((_("Update all genre in meta from eit"), boundFunction(self.updateMetaFromEit)))
        if config.AdvancedMovieSelection.showpreview.value and config.AdvancedMovieSelection.show_cover_del.value:
            if not service.flags & eServiceReference.mustDescent:
                menu.append((_("Delete cover"), boundFunction(self.deletecover)))
        if config.AdvancedMovieSelection.showpreview.value and config.AdvancedMovieSelection.show_info_del.value:
            if not service.flags & eServiceReference.mustDescent:
                menu.append((_("Delete movie info"), boundFunction(self.deleteinfos)))
        if config.AdvancedMovieSelection.showpreview.value and config.AdvancedMovieSelection.show_info_cover_del.value:
            if not service.flags & eServiceReference.mustDescent:
                menu.append((_("Delete movie info and cover"), boundFunction(self.deleteinfocover)))   
        if config.AdvancedMovieSelection.showmovietagsinmenu.value and not service.flags & eServiceReference.mustDescent:
            menu.append((_("Movie tags"), boundFunction(self.movietags)))
        if config.AdvancedMovieSelection.showfiltertags.value:
            menu.append((_("Filter by Tags"), boundFunction(self.filterbytags)))
        if config.AdvancedMovieSelection.showmenu.value and config.AdvancedMovieSelection.show_infobar_position.value:
            menu.append((_("Setup Moviebar position"), self.moviebarsetup))
        if YTTrailerPresent == True and config.AdvancedMovieSelection.showtrailer.value and not (self.service.flags & eServiceReference.mustDescent): 
            menu.append((_("Search Trailer on web"), boundFunction(self.showTrailer)))
        if config.AdvancedMovieSelection.showmenu.value:
            menu.append((_("Setup"), boundFunction(self.menusetup)))
        self["menu"] = MenuList(menu)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_("Advanced Movie Selection Menu"))

    def updateMetaFromEit(self):
        self.csel.list.updateMetaFromEit()
        self.csel.reloadList()
        self.close()
        
    def unmount(self):
        res = self.csel["list"].unmount(self.service)
        if res == 0:
            self.session.open(MessageBox, _("The device '%s' can now removed!") % (self.service.getName()), MessageBox.TYPE_INFO)
            self.csel.reloadList()
            self.close()        
        else:
            self.session.open(MessageBox, _("Error occurred during unmounting device!"), MessageBox.TYPE_ERROR)

    def waste(self):
        from Wastebasket import Wastebasket
        self.session.openWithCallback(self.closeafterfinish, Wastebasket)

    def marknewicon(self):
        self.csel.marknewicon()
        self.close() 
               
    def showTrailer(self):
        if YTTrailerPresent == True:
            from ServiceProvider import ServiceCenter
            eventname = ServiceCenter.getInstance().info(self.service).getName(self.service)
            self.session.open(YTTrailerList, eventname)
        else:
            pass

    def moviebarsetup(self):
        self.session.open(MoviebarPositionSetup)

    def checkConnection(self):
        try:
            import socket 
            print socket.gethostbyname('www.google.com')
            return True
        except:
            self.session.openWithCallback(self.close, MessageBox, _("No internet connection available!"), MessageBox.TYPE_ERROR)
            return False

    def downloadMovieInfo(self):
        if self.checkConnection() == False:
            return
        if len(self.csel.list.multiSelection) == 0:
            self.session.openWithCallback(self.closeafterfinish, DownloadMovies, self.csel.list.list, config.AdvancedMovieSelection.coversize.value, self.service)
        else:
            self.downloadSelectedMovieInfo()

    def closeafterfinish(self, retval=None):
        self.csel.updateDescription()
        self.csel.reloadList()
        self.close()        

    def downloadMovieInfoAll(self):
        if self.checkConnection() == False:
            return
        if len(self.csel.list.multiSelection) == 0:
            self.session.openWithCallback(self.closeafterfinish, DownloadMovies, self.csel.list.list, config.AdvancedMovieSelection.coversize.value)
        else:
            self.downloadSelectedMovieInfo()

    def downloadSelectedMovieInfo(self):
        items = []
        for item in self.csel.list.multiSelection:
            items.append([item, 0])
        self.session.openWithCallback(self.closeafterfinish, DownloadMovies, items, config.AdvancedMovieSelection.coversize.value)

    def retitel(self, session, service):
        self.session.openWithCallback(self.closeafterfinish, MovieRetitle, service)

    def imdbsearch(self):
        from ServiceProvider import ServiceCenter
        searchTitle = ServiceCenter.getInstance().info(self.service).getName(self.service)
        self.session.openWithCallback(self.closeafterfinish, TMDbMainsave, searchTitle, service=self.service)

    def menusetup(self):
        self.session.openWithCallback(self.cancelClick, AdvancedMovieSelectionSetup, self.csel)
        
    def setupbutton(self):
        self.session.open(AdvancedMovieSelectionButtonSetup, self.csel)

    def movecopy(self):
        if not (self.service.flags & eServiceReference.mustDescent):
            self.session.openWithCallback(self.closeafterfinish, MovieMove, self.csel, self.service)
        else:
            self.session.open(MessageBox, _("Move/Copy not possible here!"), MessageBox.TYPE_INFO)

    def movietags(self):
        self.session.open(MovieTagEditor, service=self.service, parent=self.session.current_dialog)

    def filterbytags(self):
        self.csel.showTagsSelect()
        self.csel.reloadList()
        self.close()

    def searchmovie(self):
        MovieSearchScreen(session=self.session)

    def setMovieStatus(self, status):
        self.csel.setMovieStatus(status)
        if config.AdvancedMovieSelection.shownew2.value and status == 0:
            self.marknewicon()
        self.close()

    def okbuttonClick(self):
        self["menu"].getCurrent()[1]()

    def cancelClick(self):
        #self.csel["list"].updateHotplugDevices()
        #self.csel.reloadList()
        self.close(False)

    def sortBy(self, newType):
        config.movielist.moviesort.value = newType
        self.csel.setSortType(newType)
        self.csel.reloadList()
        self.close()

    def listType(self, newType):
        config.movielist.listtype.value = newType
        self.csel.setListType(newType)
        self.csel.list.redrawList()
        self.close()

    def showDescription(self, newType):
        config.movielist.description.value = newType
        self.csel.setDescriptionState(newType)
        self.csel.updateDescription()
        self.close()

    def showFolders(self, value):
        config.AdvancedMovieSelection.showfoldersinmovielist.value = value
        config.AdvancedMovieSelection.showfoldersinmovielist.save()
        self.csel.showFolders(value)
        self.csel.reloadList()
        self.close()

    def showProgressbar(self, value):
        config.AdvancedMovieSelection.showprogessbarinmovielist.value = value
        config.AdvancedMovieSelection.showprogessbarinmovielist.save()
        self.csel.showProgressbar(value)
        self.csel.reloadList()
        self.close()

    def showStatusIcon(self, value):
        config.AdvancedMovieSelection.showiconstatusinmovielist.value = value
        config.AdvancedMovieSelection.showiconstatusinmovielist.save()
        self.csel.showStatusIcon(value)
        self.csel.reloadList()
        self.close()

    def showStatusColor(self, value):
        config.AdvancedMovieSelection.showcolorstatusinmovielist.value = value
        config.AdvancedMovieSelection.showcolorstatusinmovielist.save()
        self.csel.showStatusColor(value)
        self.csel.reloadList()
        self.close()
        
    def showDate(self, value):
        config.movielist.showdate.value = value
        config.movielist.showdate.save()
        self.csel.showDate(value)
        self.csel.reloadList()
        self.close()
        
    def showTime(self, value):
        config.movielist.showtime.value = value
        config.movielist.showtime.save()
        self.csel.showTime(value)
        self.csel.reloadList()
        self.close()

    def showTags(self, value):
        config.movielist.showtags.value = value
        config.movielist.showtags.save()
        self.csel.showTags(value)
        self.csel.reloadList()
        self.close()
        
    def showService(self, value):
        config.movielist.showservice.value = value
        config.movielist.showservice.save()
        self.csel.showService(value)
        self.csel.reloadList()
        self.close()

    def execPlugin(self, plugin):
        if not (self.service.flags & eServiceReference.mustDescent):
            plugin(session=self.session, service=self.service)

    def delete(self):
        self.csel.delete()
        self.close()
    
    def deleteinfocover(self):
        serviceHandler = eServiceCenter.getInstance()
        offline = serviceHandler.offlineOperations(self.service)
        info = serviceHandler.info(self.service)
        name = info and info.getName(self.service) or _("this recording")
        result = False
        if self.service.flags & eServiceReference.mustDescent:
            if self.service.getName() != "..":
                result = True
                name = self.service.getPath()
        else:
            if offline is not None:
                if not offline.deleteFromDisk(1):
                    result = True
        if result == True:
            if config.AdvancedMovieSelection.askdelete.value:
                self.session.openWithCallback(self.deleteinfocoverConfirmed, MessageBox, _("Do you really want to delete info/cover from:\n%s?") % (name))
            else:
                self.deleteinfocoverConfirmed(True)
        else:
            self.session.openWithCallback(self.close, MessageBox, _("You cannot delete this!"), MessageBox.TYPE_ERROR)

    def deleteinfocoverConfirmed(self, confirmed):
        if not confirmed:
            return self.close()
        try:
            title = self.service.getPath()
            if title.endswith(".ts"):
                movietitle = title[:-3]
            elif title.endswith(".mp4") or title.endswith(".avi") or title.endswith(".mkv") or title.endswith(".mov") or title.endswith(".flv") or title.endswith(".m4v") or title.endswith(".mpg") or title.endswith(".iso"):
                movietitle = title[:-4]
            elif title.endswith(".divx") or title.endswith(".m2ts") or title.endswith(".mpeg"):
                movietitle = title[:-5]
            else:
                movietitle = title
            eConsoleAppContainer().execute("rm -f '%s'" % movietitle + ".eit")
            eConsoleAppContainer().execute("rm -f '%s'" % movietitle + ".jpg")
            self.csel.updateDescription()
            self.csel["freeDiskSpace"].update()
            self.close()
        except:
            pass

    def deletecover(self):
        serviceHandler = eServiceCenter.getInstance()
        offline = serviceHandler.offlineOperations(self.service)
        info = serviceHandler.info(self.service)
        name = info and info.getName(self.service) or _("this recording")
        result = False
        if self.service.flags & eServiceReference.mustDescent:
            if self.service.getName() != "..":
                result = True
                name = self.service.getPath()
        else:
            if offline is not None:
                if not offline.deleteFromDisk(1):
                    result = True
        if result == True:
            if config.AdvancedMovieSelection.askdelete.value:
                self.session.openWithCallback(self.deletecoverConfirmed, MessageBox, _("Do you really want to delete cover from:\n%s?") % (name))
            else:
                self.deletecoverConfirmed(True)
        else:
            self.session.openWithCallback(self.close, MessageBox, _("You cannot delete this!"), MessageBox.TYPE_ERROR)

    def deletecoverConfirmed(self, confirmed):
        if not confirmed:
            return self.close()
        try:
            title = self.service.getPath()
            if title.endswith(".ts"):
                movietitle = title[:-3]
            elif title.endswith(".mp4") or title.endswith(".avi") or title.endswith(".mkv") or title.endswith(".mov") or title.endswith(".flv") or title.endswith(".m4v") or title.endswith(".mpg") or title.endswith(".iso"):
                movietitle = title[:-4]
            elif title.endswith(".divx") or title.endswith(".m2ts") or title.endswith(".mpeg"):
                movietitle = title[:-5]
            else:
                movietitle = title
            eConsoleAppContainer().execute("rm -f '%s'" % movietitle + ".jpg")
            self.csel.updateDescription()
            self.csel["freeDiskSpace"].update()
            self.close()
        except:
            pass

    def deleteinfos(self):
        serviceHandler = eServiceCenter.getInstance()
        offline = serviceHandler.offlineOperations(self.service)
        info = serviceHandler.info(self.service)
        name = info and info.getName(self.service) or _("this recording")
        result = False
        if self.service.flags & eServiceReference.mustDescent:
            if self.service.getName() != "..":
                result = True
                name = self.service.getPath()
        else:
            if offline is not None:
                if not offline.deleteFromDisk(1):
                    result = True
        if result == True:
            if config.AdvancedMovieSelection.askdelete.value:
                self.session.openWithCallback(self.deleteinfosConfirmed, MessageBox, _("Do you really want to delete movie info from:\n%s?") % (name))
            else:
                self.deleteinfosConfirmed(True)
        else:
            self.session.openWithCallback(self.close, MessageBox, _("You cannot delete this!"), MessageBox.TYPE_ERROR)

    def deleteinfosConfirmed(self, confirmed):
        if not confirmed:
            return self.close()
        try:
            title = self.service.getPath()
            if title.endswith(".ts"):
                movietitle = title[:-3]
            elif title.endswith(".mp4") or title.endswith(".avi") or title.endswith(".mkv") or title.endswith(".mov") or title.endswith(".flv") or title.endswith(".m4v") or title.endswith(".mpg") or title.endswith(".iso"):
                movietitle = title[:-4]
            elif title.endswith(".divx") or title.endswith(".m2ts") or title.endswith(".mpeg"):
                movietitle = title[:-5]
            else:
                movietitle = title
            eConsoleAppContainer().execute("rm -f '%s'" % movietitle + ".eit")
            self.csel.updateDescription()
            self.csel["freeDiskSpace"].update()
            self.close()
        except:
            pass

class SelectionEventInfo:
    def __init__(self):
        self["Service"] = ServiceEvent()
        self.list.connectSelChanged(self.__selectionChanged)
        self.timer = eTimer()
        self.timer.callback.append(self.updateEventInfo)
        self.onShown.append(self.__selectionChanged)

    def __selectionChanged(self):
        if self.execing and config.movielist.description.value == MovieList.SHOW_DESCRIPTION:
            self.timer.start(100, True)

    def updateEventInfo(self):
        evt = self["list"].getCurrentEvent()
        serviceref = self.getCurrent()
        if evt:
            self["Service"].newService(serviceref)
        else:
            self["Service"].newService(None)
        self.updateName()
        if config.AdvancedMovieSelection.showpreview.value == True:
            self.loadPreview(serviceref)

class AdvancedMovieSelection_summary(Screen):
    def __init__(self, session, parent):
        self.skinName = ["AdvancedMovieSelection_summary"]
        Screen.__init__(self, session, parent)
        self["ShortDesc"] = Label("")
        self["Seperator"] = StaticText("")
       
    def updateShortDescription(self, desc):
        self["ShortDesc"].setText(desc)

    def showSeperator(self):
        self["Seperator"].setText(resolveFilename(SCOPE_CURRENT_SKIN, "images/sep_lcd_oled.png"))
    
    def hideSeperator(self):
        self["Seperator"].setText("")    

class MovieSelection(Screen, HelpableScreen, SelectionEventInfo, MoviePreview, QuickButton):
    def __init__(self, session, selectedmovie=None, showLastDir=False):
        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        MoviePreview.__init__(self, session)
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if config.AdvancedMovieSelection.showpreview.value and config.AdvancedMovieSelection.minitv.value:
            if sz_w == 1280:
                self.skinName = ["AdvancedMovieSelectionHD", "AdvancedMovieSelection"]
            elif sz_w == 1024:
                self.skinName = ["AdvancedMovieSelectionXD", "AdvancedMovieSelection"]
            else:
                self.skinName = ["AdvancedMovieSelectionSD", "AdvancedMovieSelection"]
        if not config.AdvancedMovieSelection.showpreview.value and config.AdvancedMovieSelection.minitv.value:
            if sz_w == 1280:
                self.skinName = ["AdvancedMovieSelection1HD", "AdvancedMovieSelection"]
            elif sz_w == 1024:
                self.skinName = ["AdvancedMovieSelection1XD", "AdvancedMovieSelection"]
            else:
                self.skinName = ["AdvancedMovieSelection1SD", "AdvancedMovieSelection"]            
        if config.AdvancedMovieSelection.showpreview.value and not config.AdvancedMovieSelection.minitv.value:
            if sz_w == 1280:
                self.skinName = ["AdvancedMovieSelection_noMiniTV_HD", "AdvancedMovieSelection"]
            elif sz_w == 1024:
                self.skinName = ["AdvancedMovieSelection_noMiniTV_XD", "AdvancedMovieSelection"]
            else:
                self.skinName = ["AdvancedMovieSelection_noMiniTV_SD", "AdvancedMovieSelection"]
        if not config.AdvancedMovieSelection.showpreview.value and not config.AdvancedMovieSelection.minitv.value:
            if sz_w == 1280:
                self.skinName = ["AdvancedMovieSelection1_noMiniTV_HD", "AdvancedMovieSelection"]
            elif sz_w == 1024:
                self.skinName = ["AdvancedMovieSelection1_noMiniTV_XD", "AdvancedMovieSelection"]
            else:
                self.skinName = ["AdvancedMovieSelection1_noMiniTV_SD", "AdvancedMovieSelection"]
        self.tags = [ ]
        if selectedmovie:
            self.selected_tags = config.movielist.last_selected_tags.value
        else:
            self.selected_tags = None
        self.selected_tags_ele = None

        self.movemode = False
        self.bouquet_mark_edit = False

        self.delayTimer = eTimer()
        self.delayTimer.callback.append(self.updateHDDData)

        self["waitingtext"] = Label(_("Please wait... Loading list..."))
        self["DescriptionBorder"] = Pixmap()
        self["DescriptionBorder"].hide()
        self["warning"] = Label()
        if not config.AdvancedMovieSelection.askdelete.value:
            if config.AdvancedMovieSelection.showinfo.value:
                self["warning"].setText(_("ATTENTION: Ask before delete is disabled!"))

        if not config.AdvancedMovieSelection.startdir.value and not showLastDir:
            if path.exists(config.movielist.last_videodir.value):
                config.movielist.last_videodir.value = defaultMoviePath()
                config.movielist.last_videodir.save()
        if not path.exists(config.movielist.last_videodir.value):
            config.movielist.last_videodir.value = "/media/"
            config.movielist.last_videodir.save()

        self.current_ref = eServiceReference("2:0:1:0:0:0:0:0:0:0:" + config.movielist.last_videodir.value)            

        self["list"] = MovieList(None,
            config.movielist.listtype.value,
            config.movielist.moviesort.value,
            config.movielist.description.value,
            config.AdvancedMovieSelection.showfoldersinmovielist.value,
            config.AdvancedMovieSelection.showprogessbarinmovielist.value,
            config.AdvancedMovieSelection.showiconstatusinmovielist.value,
            config.AdvancedMovieSelection.showcolorstatusinmovielist.value,
            config.movielist.showdate.value,
            config.movielist.showtime.value,
            config.movielist.showservice.value,
            config.movielist.showtags.value)
        self.list = self["list"]
        self.selectedmovie = selectedmovie
        SelectionEventInfo.__init__(self)
        self["MovieService"] = ServiceEvent()
        self["MovieSize"] = ServiceEvent()
        self["Movietitle"] = StaticText()
        self["Movielocation"] = StaticText()
        self["freeDiskSpace"] = self.diskinfo = DiskInfo(config.movielist.last_videodir.value, DiskInfo.FREE, update=False)
        self["InfobarActions"] = HelpableActionMap(self, "InfobarActions",
            {
                "showMovies": (self.doPathSelect, _("Select the movie path")),
                "showRadio": (self.radioButton, _("Multiselection")),
            })
        self["MovieSelectionActions"] = HelpableActionMap(self, "MovieSelectionActions",
            {
                "contextMenu": (self.doContext, _("Advanced movielist menu")),
                "showEventInfo": (self.showEventInformation, _("Show event details")),
            })
        self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
            {
                "cancel": (self.abort, _("Exit movielist")),
                "ok": (self.movieSelected, _("Select movie")),
            })
        QuickButton.__init__(self)
        self.onShown.append(self.go)
        self.onLayoutFinish.append(self.saveListsize)
        self.inited = False

    def createSummary(self):
        return AdvancedMovieSelection_summary
        
    def radioButton(self):
        if self.list.toggleSelection():
            #self.list.moveDown()
            idx = self.list.getCurrentIndex()
            self.list.moveToIndex(min(idx + 1, len(self.list.list) - 1))

    def getTrashMessage(self, qty, waste, recording, name=""):
        if qty == 1:
            if waste:
                if recording:
                    return (_("%s is currently recording!") % (name) + _("\n\nThe timer for %s will be delete for stop the recording and after this the movie will be move to trashcan.\n\nDo you really want to continue?") % (name))
                else:
                    return _("Do you really want to move %s to trashcan?") % (name)
            else:
                if recording:
                    return (_("%s is currently recording!") % (name) + _("\n\nThe timer for %s will be delete for stop the recording and after this the movie will be deleted.\n\nDo you really want to continue?") % (name))
                else:
                    return _("Do you really want to delete %s?") % (name)
        else:
            timer_text = recording and _("Recordings are active, the timer(s) will also be deleted!\n") or ""
            if waste: 
                return timer_text + _("Do you really want to move selected movies to trashcan?")
            else:
                return timer_text + _("Do you really want to delete selected movies?")

    def delete(self):
        self.service = self.getCurrent()
        if self.service.flags & eServiceReference.mustDescent and not isinstance(self.service, eServiceReferenceDvd):
            if config.AdvancedMovieSelection.showinfo.value:
                self.session.open(MessageBox, _("This cannot deleted, please select a movie for!"), MessageBox.TYPE_INFO)
                return

        if len(self.list.multiSelection) > 0:
            self.to_delete = self.list.multiSelection[:]
        else:
            self.to_delete = [self.service]
        
        serviceHandler = eServiceCenter.getInstance()
        offline = serviceHandler.offlineOperations(self.service)
        info = serviceHandler.info(self.service)
        name = info and info.getName(self.service) or _("this recording")

        recording = False
        if NavigationInstance.instance.getRecordings():
            for timer in NavigationInstance.instance.RecordTimer.timer_list:
                if timer.state == TimerEntry.StateRunning:
                    try:
                        filename = "%s.ts" % timer.Filename
                    except:
                        filename = ""
                    for serviceref in self.to_delete:
                        if filename and os.path.realpath(filename) == os.path.realpath(serviceref.getPath()):
                            recording = True
                            continue
  
        result = False
        if self.service.flags & eServiceReference.mustDescent:
            if self.service.getName() != "..":
                result = True
                name = self.service.getPath()
        else:
            if offline is not None:
                if not offline.deleteFromDisk(1):
                    result = True

        if result == True:
            if not config.AdvancedMovieSelection.askdelete.value:
                self.deleteConfirmed(True)
            else:
                text = self.getTrashMessage(len(self.to_delete), config.AdvancedMovieSelection.use_wastebasket.value, recording, name)
                self.session.openWithCallback(self.deleteTrashConfirmed, MessageBox, text)
        else:
            self.session.open(MessageBox, _("You cannot delete this!"), MessageBox.TYPE_ERROR)

    def stopRemoveTimer(self, file_path):
        if NavigationInstance.instance.getRecordings():
            for timer in NavigationInstance.instance.RecordTimer.timer_list:
                if timer.isRunning():
                    try:
                        filename = "%s.ts" % timer.Filename
                    except:
                        filename = ""
                    if filename and os.path.realpath(filename) == os.path.realpath(file_path):
                        timer.afterEvent = AFTEREVENT.NONE
                        timer.abort()
                        if timer.repeated == 0:
                            self.session.nav.RecordTimer.removeEntry(timer)
                        return
        
    def deleteTrashConfirmed(self, confirmed):
        if not confirmed:
            return
        try:
            for item in self.to_delete:
                self.stopRemoveTimer(item.getPath())
                Trashcan.trash(item.getPath())
                self["list"].removeService(item)
        except Exception, e:
            print e
            self.session.open(MessageBox, _("Delete failed!"), MessageBox.TYPE_ERROR)
        self["freeDiskSpace"].update()

    def deleteConfirmed(self, confirmed):
        if not confirmed:
            return

        if config.AdvancedMovieSelection.use_wastebasket.value:
            self.deleteTrashConfirmed(confirmed)
            return
        
        for item in self.to_delete:
            result = False
            try:
                self.stopRemoveTimer(item.getPath())
                title = item.getPath()
                if path.isfile(item.getPath()):
                    title = path.splitext(item.getPath())[0]
                    serviceHandler = eServiceCenter.getInstance()
                    offline = serviceHandler.offlineOperations(item)
                    if offline is not None:
                        if not offline.deleteFromDisk(0):
                            result = True
                else:
                    eConsoleAppContainer().execute("rm -rf '%s'" % item.getPath())
                print title
    
                eConsoleAppContainer().execute("rm -f '%s'" % title + ".cuts")
                eConsoleAppContainer().execute("rm -f '%s'" % title + ".eit")
                eConsoleAppContainer().execute("rm -f '%s'" % title + ".jpg")
                eConsoleAppContainer().execute("rm -f '%s'" % title + "*.ts.meta")
                eConsoleAppContainer().execute("rm -f '%s'" % title + ".ts.cutsr")
                eConsoleAppContainer().execute("rm -f '%s'" % title + ".ts.gm")        
                eConsoleAppContainer().execute("rm -f '%s'" % title + ".ts.sc")
                eConsoleAppContainer().execute("rm -f '%s'" % title + ".ts.ap")
                eConsoleAppContainer().execute("rm -f '%s'" % title)
                result = True
            except Exception, e:
                print "Exception deleting files: " + str(e)
    
            if result == False:
                self.session.open(MessageBox, _("Delete failed!"), MessageBox.TYPE_ERROR)
                return
            else:
                self["list"].removeService(item)
                self["freeDiskSpace"].update()

    def updateCurrentSelection(self, dummy=None):
        self.list.updateCurrentSelection()

    def updateName(self):
        location = (_("Movie location: %s") % config.movielist.last_videodir.value)
        self["Movielocation"].setText(location)
        serviceref = self.getCurrent()
        self["MovieSize"].newService(serviceref)
        event = self["list"].getCurrentEvent()
        info = self["list"].getCurrentInfo()
        if event is not None:
            moviename = event.getEventName()
            self["Movietitle"].setText(moviename)
            self["MovieService"].newService(serviceref)
            desc = event.getShortDescription()        
            if moviename == desc or desc == "":
                if config.AdvancedMovieSelection.show_date_shortdesc.value and config.AdvancedMovieSelection.show_begintime.value:
                    desc = getBeginTimeString(info, serviceref)
                    self.summaries.showSeperator()
                    self.summaries.updateShortDescription(desc)
                elif config.AdvancedMovieSelection.show_date_shortdesc.value and not config.AdvancedMovieSelection.show_begintime.value:
                    desc = getDateString()
                    self.summaries.showSeperator()
                    self.summaries.updateShortDescription(desc)
                else:
                    desc = ""
                    self.summaries.hideSeperator()
                    self.summaries.updateShortDescription(desc)
            else:
                self.summaries.showSeperator()
                self.summaries.updateShortDescription(desc)
        else:
            desc = ""
            self.summaries.hideSeperator()
            self.summaries.updateShortDescription(desc)
            self["Movietitle"].setText(_("Advanced Movie Selection"))
            self["MovieService"].newService(None)
            self["MovieSize"].newService(None)

    def updateDescription(self):
        if config.movielist.description.value == MovieList.SHOW_DESCRIPTION:
            self["DescriptionBorder"].show()
            self["list"].instance.resize(eSize(self.listWidth, self.listHeight - self["DescriptionBorder"].instance.size().height()))
        else:
            self["Service"].newService(None)
            self["DescriptionBorder"].hide()
            self["list"].instance.resize(eSize(self.listWidth, self.listHeight))

    def showEventInformation(self):
        if IMDbPresent and OFDbPresent and TMDbPresent and config.AdvancedMovieSelection.Eventinfotyp.value == "Ei":
            self.showConfirmedInfo([None, "Ei"])
        elif IMDbPresent and OFDbPresent and TMDbPresent and config.AdvancedMovieSelection.Eventinfotyp.value == "Ti":
            self.showConfirmedInfo([None, "Ti"])
        elif IMDbPresent and OFDbPresent and TMDbPresent and config.AdvancedMovieSelection.Eventinfotyp.value == "Ii":
            self.showConfirmedInfo([None, "Ii"])
        elif IMDbPresent and OFDbPresent and TMDbPresent and config.AdvancedMovieSelection.Eventinfotyp.value == "Oi":
            self.showConfirmedInfo([None, "Oi"])
        else:
            if IMDbPresent and not OFDbPresent and not TMDbPresent and config.AdvancedMovieSelection.Eventinfotyp2.value == "Ei":
                self.showConfirmedInfo([None, "Ei"])
            elif IMDbPresent and not OFDbPresent and not TMDbPresent and config.AdvancedMovieSelection.Eventinfotyp2.value == "Ii":
                self.showConfirmedInfo([None, "Ii"])
            else:
                if OFDbPresent and not IMDbPresent and not TMDbPresent and config.AdvancedMovieSelection.Eventinfotyp3.value == "Ei":
                    self.showConfirmedInfo([None, "Ei"])
                elif OFDbPresent and not IMDbPresent and not TMDbPresent and config.AdvancedMovieSelection.Eventinfotyp3.value == "Oi":
                    self.showConfirmedInfo([None, "Oi"])
                else:
                    if TMDbPresent and not OFDbPresent and not IMDbPresent and config.AdvancedMovieSelection.Eventinfotyp4.value == "Ei":
                        self.showConfirmedInfo([None, "Ei"])
                    elif TMDbPresent and not OFDbPresent and not IMDbPresent and config.AdvancedMovieSelection.Eventinfotyp4.value == "Ti":
                        self.showConfirmedInfo([None, "Ti"])
                    else:
                        if TMDbPresent and not OFDbPresent and IMDbPresent and config.AdvancedMovieSelection.Eventinfotyp5.value == "Ei":
                            self.showConfirmedInfo([None, "Ei"])
                        elif TMDbPresent and not OFDbPresent and IMDbPresent and config.AdvancedMovieSelection.Eventinfotyp5.value == "Ti":
                            self.showConfirmedInfo([None, "Ti"])
                        elif TMDbPresent and not OFDbPresent and IMDbPresent and config.AdvancedMovieSelection.Eventinfotyp5.value == "Ii":
                            self.showConfirmedInfo([None, "Ii"])
                        else:
                            if TMDbPresent and OFDbPresent and not IMDbPresent and config.AdvancedMovieSelection.Eventinfotyp6.value == "Ei":
                                self.showConfirmedInfo([None, "Ei"])
                            elif TMDbPresent and OFDbPresent and not IMDbPresent and config.AdvancedMovieSelection.Eventinfotyp6.value == "Ti":
                                self.showConfirmedInfo([None, "Ti"])
                            elif TMDbPresent and OFDbPresent and not IMDbPresent and config.AdvancedMovieSelection.Eventinfotyp6.value == "Oi":
                                self.showConfirmedInfo([None, "Oi"])
                            else:
                                if not TMDbPresent and OFDbPresent and IMDbPresent and config.AdvancedMovieSelection.Eventinfotyp7.value == "Ei":
                                    self.showConfirmedInfo([None, "Ei"])
                                elif not TMDbPresent and OFDbPresent and IMDbPresent and config.AdvancedMovieSelection.Eventinfotyp7.value == "Ii":
                                    self.showConfirmedInfo([None, "Ii"])
                                elif not TMDbPresent and OFDbPresent and IMDbPresent and config.AdvancedMovieSelection.Eventinfotyp7.value == "Oi":
                                    self.showConfirmedInfo([None, "Oi"])
                                else:
                                    self.showConfirmedInfo([None, "Ei"])

    def showConfirmedInfo(self, answer):
        event = self["list"].getCurrentEvent()
        answer = answer and answer[1]
        if answer == "Ei":
            if event is not None:
                from AdvancedMovieSelectionEventView import EventViewSimple
                from ServiceReference import ServiceReference
                serviceref = self.getCurrent()
                evt = self["list"].getCurrentEvent()
                if evt:
                    self.session.open(EventViewSimple, evt, serviceref, ServiceReference(self.getCurrent()))
        if answer == "Ii":
            if event is not None:
                IeventName = event.getEventName()
                self.session.open(IMDB, IeventName)
        if answer == "Oi":
            if event is not None:
                IeventName = event.getEventName()
                self.session.open(OFDB, IeventName)
        if answer == "Ti":
            if event is not None:
                eventName = event.getEventName()
                self.session.open(TMDbMain, eventName) 

    def go(self):
        if not self.inited:
        # ouch. this should redraw our "Please wait..."-text.
        # this is of course not the right way to do this.
            self.delayTimer.start(10, 1)
            self.inited = True

    def saveListsize(self):
        listsize = self["list"].instance.size()
        self.listWidth = listsize.width()
        self.listHeight = listsize.height()
        self.updateDescription()

    def updateHDDData(self):
        self.reloadList(self.selectedmovie)
        self["waitingtext"].visible = False

    def moveTo(self):
        self["list"].moveTo(self.selectedmovie)

    def getCurrent(self):
        self.session.currentSelection = self["list"].getCurrent()
        return self.session.currentSelection

    def setMovieStatus(self, status):
        if config.AdvancedMovieSelection.shownew2.value and status == 0:
            self.marknewicon()
        current = self.getCurrent()
        if current is not None:
            self["list"].setMovieStatus(current, status)

    def marknewicon(self):
        self.service = self.getCurrent()
        moviename = self.service.getPath()
        if moviename.endswith(".ts"):
            movietitle = moviename + ".gm"
            filehandle = open(movietitle, "w")
            filehandle.write(movietitle)
            filehandle.close()

    def movieSelected(self):
        current = self.getCurrent()
        if current is not None:
            if current.flags & eServiceReference.mustDescent:
                self.gotFilename(current.getPath())
            else:
                self.saveconfig()
                from plugin import PlayerInstance
                if isinstance(current, eServiceReferenceDvd):
                    from plugin import movieSelected
                    movieSelected(self, current)
                    current = None
                elif PlayerInstance is not None:
                    PlayerInstance.playerClosed(current)
                self.close(current)

    def doContext(self, retval=None):
        current = self.getCurrent()
        if current is not None:
            if not config.usage.load_length_of_movies_in_moviellist.value:
                self.session.open(MovieContextMenu, self, current)
            else:
                self.session.openWithCallback(self.checkchanges, MovieContextMenu, self, current)

    def checkchanges(self, retval=None):
        if not config.usage.load_length_of_movies_in_moviellist.value:
            self.session.openWithCallback(self.abort, MessageBox, _("Load Length of Movies in Movielist has been disabled.\nClose and reopen Movielist is required to apply the setting."), MessageBox.TYPE_INFO)

    def abort(self, retval=None):
        self.saveconfig()
        self.close(None)

    def saveconfig(self):
        config.movielist.last_selected_tags.value = self.selected_tags
        config.movielist.moviesort.save()
        config.movielist.listtype.save()
        config.movielist.description.save()
        config.movielist.showdate.save()
        config.movielist.showtime.save()
        config.movielist.showservice.save()
        config.movielist.showtags.save()
        config.AdvancedMovieSelection.show_bookmarks.save()

    def showTrailer(self):
        if YTTrailerPresent == True:
            event = self["list"].getCurrentEvent()
            if event is not None:
                eventname = event.getEventName()
                self.session.open(YTTrailerList, eventname)
            else:
                pass
        else:
            pass

    def getTagDescription(self, tag):
        # TODO: access the tag database
        return tag

    def updateTags(self):
        # get a list of tags available in this list
        self.tags = list(self["list"].tags)
        # insert text for selecting all movies
        self.tags.insert(0, _(SHOW_ALL_MOVIES))
        
        if not self.tags:
            # by default, we do not display any filtering options
            self.tag_first = ""
            self.tag_second = ""
        else:
            tmp = config.movielist.first_tags.value
            if tmp in self.tags:
                self.tag_first = tmp
            else:
                self.tag_first = "<" + _("Tag 1") + ">"
            tmp = config.movielist.second_tags.value
            if tmp in self.tags:
                self.tag_second = tmp
            else:
                self.tag_second = "<" + _("Tag 2") + ">"

        #self["key_green"].text = self.tag_first
        #self["key_yellow"].text = self.tag_second
        
        # the rest is presented in a list, available on the
        # fourth ("blue") button
        #if self.tags:
        #    self["key_blue"].text = _("Tags") + "..."
        #else:
        #    self["key_blue"].text = ""

    def setListType(self, type):
        self["list"].setListType(type)

    def setDescriptionState(self, val):
        self["list"].setDescriptionState(val)

    def setSortType(self, type):
        self["list"].setSortType(type)

    def showFolders(self, val):
        self["list"].showFolders(val)

    def showProgressbar(self, value):
        self["list"].showProgressbar(value)

    def showStatusIcon(self, value):
        self["list"].showStatusIcon(value)

    def showStatusColor(self, value):
        self["list"].showStatusColor(value)
        
    def showDate(self, value):
        self["list"].showDate(value)
        
    def showTime(self, value):
        self["list"].showTime(value)
        
    def showService(self, value):
        self["list"].showService(value)

    def showTags(self, value):
        self["list"].showTags(value)

    def reloadList(self, sel=None, home=False):
        if not fileExists(config.movielist.last_videodir.value):
            path = defaultMoviePath()
            config.movielist.last_videodir.value = path
            config.movielist.last_videodir.save()
            self.current_ref = eServiceReference("2:0:1:0:0:0:0:0:0:0:" + path)
            self["freeDiskSpace"].path = path
        if sel is None:
            sel = self.getCurrent()
        self["list"].reload(self.current_ref, self.selected_tags)
        title = _("Movie location:")
        #if config.usage.setup_level.index >= 2: # expert+
        title += "  " + config.movielist.last_videodir.value
        if self.selected_tags is not None:
            title += " - " + ','.join(self.selected_tags)
        self.setTitle(title)
        if not (sel and self["list"].moveTo(sel)):
            if home:
                self["list"].moveToIndex(0)
        self.updateTags()
        self["freeDiskSpace"].update()

    def doPathSelect(self):
        self.session.openWithCallback(
            self.gotFilename,
            MovieLocationBox,
            _("Please select the movie path..."),
            config.movielist.last_videodir.value
        )

    def gotFilename(self, res):
        if res is not None and res is not config.movielist.last_videodir.value:
            if fileExists(res):           
                selection = None
                current = self.getCurrent()
                if current is not None:
                    if current.flags & eServiceReference.mustDescent:                
                        if current.getName() == "..":
                            selection = eServiceReference("2:47:1:0:0:0:0:0:0:0:" + self["list"].root.getPath())
                            
                config.movielist.last_videodir.value = res
                config.movielist.last_videodir.save()
                self.current_ref = eServiceReference("2:0:1:0:0:0:0:0:0:0:" + res)
                self["freeDiskSpace"].path = res
                self.reloadList(sel=selection, home=True)
            else:
                self.session.open(
                    MessageBox,
                    _("Directory %s nonexistent.") % (res),
                    type=MessageBox.TYPE_ERROR,
                    timeout=5
                    )

    def showAll(self):
        self.selected_tags_ele = None
        self.selected_tags = None
        self.reloadList(home=True)

    def showTagsN(self, tagele):
        if not self.tags:
            self.showTagWarning()
        elif not tagele or (self.selected_tags and tagele.value in self.selected_tags) or not tagele.value in self.tags:
            self.showTagsMenu(tagele)
        else:
            self.selected_tags_ele = tagele
            self.selected_tags = set([tagele.value])
            self.reloadList(home=True)

    def showTagsFirst(self):
        self.showTagsN(config.movielist.first_tags)

    def showTagsSecond(self):
        self.showTagsN(config.movielist.second_tags)

    def showTagsSelect(self):
        self.showTagsN(None)

    def tagChosen(self, tag):
        if tag and tag[0] == _(SHOW_ALL_MOVIES):
            self.showAll()
            return
        if tag is not None:
            self.selected_tags = set([tag[0]])
            if self.selected_tags_ele:
                self.selected_tags_ele.value = tag[0]
                self.selected_tags_ele.save()
            self.reloadList(home=True)

    def showTagsMenu(self, tagele):
        self.selected_tags_ele = tagele
        list = [(tag, self.getTagDescription(tag)) for tag in self.tags ]
        self.session.openWithCallback(self.tagChosen, ChoiceBox, title=_("Please select tag to filter..."), list=list)

    def showTagWarning(self):
        self.session.open(MessageBox, _("No tags are set on these movies."), MessageBox.TYPE_ERROR)
        
    def movietags(self):
        service = self.getCurrent()
        self.session.openWithCallback(self.reloadList, MovieTagEditor, service, parent=self.session.current_dialog)
        
class MoviebarPositionSetupText(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            self.skinName = ["AdvancedMovieSelectionMoviebarPositionSetupHD"]
        elif sz_w == 1024:
            self.skinName = ["AdvancedMovieSelectionMoviebarPositionSetupXD"]
        else:
            self.skinName = ["AdvancedMovieSelectionMoviebarPositionSetupSD"] 
        self["howtotext"] = StaticText(_("Use direction keys to move the Moviebar.\nPress OK button for save or the EXIT button to cancel.\nUse the red button for reset to the original position."))

class MoviebarPositionSetup(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions"],
        {
            "ok": self.go,
            "back": self.cancel,
            "up": self.up,
            "down": self.down,
            "left": self.left,
            "right": self.right,
            "red": self.red,
        }, -1)
        self.skinName = "MoviePlayer"
        self.onExecBegin.append(self.__onExecBegin)

    def __onExecBegin(self):
        self.orgpos = self.instance.position()
        offsetX = config.AdvancedMovieSelection.movieplayer_infobar_position_offset_x.value
        offsetY = config.AdvancedMovieSelection.movieplayer_infobar_position_offset_y.value
        self.instance.move(ePoint(self.orgpos.x() + offsetX, self.orgpos.y() + offsetY))
        self.screenMoviebarPositionSetupText = self.session.instantiateDialog(MoviebarPositionSetupText)
        self.screenMoviebarPositionSetupText.show()


    def red(self):
        self.instance.move(ePoint(self.orgpos.x(), self.orgpos.y()))
        print "[InfobarPositionSetup] New skin position: x = %d, y = %d" % (self.instance.position().x(), self.instance.position().y())
        
    def go(self):
        config.AdvancedMovieSelection.movieplayer_infobar_position_offset_x.value = self.instance.position().x() - self.orgpos.x()
        config.AdvancedMovieSelection.movieplayer_infobar_position_offset_x.save()
        config.AdvancedMovieSelection.movieplayer_infobar_position_offset_y.value = self.instance.position().y() - self.orgpos.y()
        config.AdvancedMovieSelection.movieplayer_infobar_position_offset_y.save()
        self.screenMoviebarPositionSetupText.doClose()
        self.close()
    
    def cancel(self):
        self.screenMoviebarPositionSetupText.doClose()
        self.close()
    
    def moveRelative(self, x=0, y=0):
        self.instance.move(ePoint(self.instance.position().x() + x, self.instance.position().y() + y))
        print "[InfobarPositionSetup] New skin position: x = %d, y = %d" % (self.instance.position().x() + x, self.instance.position().y() + y)
    
    def up(self):
        self.moveRelative(y= -2)

    def down(self):
        self.moveRelative(y=2)
    
    def left(self):
        self.moveRelative(x= -2)
    
    def right(self):
        self.moveRelative(x=2)
