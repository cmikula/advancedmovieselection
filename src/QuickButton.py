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
from Components.config import config
from Components.ActionMap import HelpableActionMap
from Components.Button import Button
from MovieList import MovieList, accessRestriction
from Components.PluginComponent import plugins
from Plugins.Plugin import PluginDescriptor
from MoveCopy import MovieMove
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Rename import MovieRetitle
from Wastebasket import Wastebasket

def getPluginCaption(pname):
    if pname != "Nothing":
        if pname == "Home":
            return _(config.AdvancedMovieSelection.hometext.value)
        elif pname == "Bookmark 1":
            return _(config.AdvancedMovieSelection.bookmark1text.value)
        elif pname == "Bookmark 2":
            return _(config.AdvancedMovieSelection.bookmark2text.value)
        elif pname == "Bookmark 3":
            return _(config.AdvancedMovieSelection.bookmark3text.value)
        elif pname == "Show/Hide folders":
            if not config.AdvancedMovieSelection.showfoldersinmovielist.value:
                return _("Show folders")
            else:
                return _("Hide folders")
        if pname == "Show up to VSR-X":
            return (_("Show up to VSR-%d") % accessRestriction.getAccess())
        if pname == "Toggle seen":
            return _("Mark as seen")
        elif pname == "Bookmark(s) on/off":
            if not config.AdvancedMovieSelection.show_bookmarks.value:
                return _("Show bookmarks")
            else:
                return _("Hide bookmarks")
        elif pname == "Sort":
            if config.movielist.moviesort.value == MovieList.SORT_ALPHANUMERIC:
                return _("Sort by Description")
            if config.movielist.moviesort.value == MovieList.SORT_DESCRIPTION:
                return _("Sort by Date (1->9)")
            if config.movielist.moviesort.value == MovieList.SORT_DATE_DESC:
                return _("Sort by Date (9->1)")
            if config.movielist.moviesort.value == MovieList.SORT_DATE_ASC:
                return _("Sort alphabetically")
        else:
            for p in plugins.getPlugins(where=[PluginDescriptor.WHERE_MOVIELIST]):
                if pname == str(p.name):
                    if config.AdvancedMovieSelection.buttoncaption.value == config.AdvancedMovieSelection.buttoncaption.default:
                        return p.name
                    else:
                        return p.description
        return _(pname)
    return ""

toggleSeenButton = None

class QuickButton:
    def __init__(self):
        self["key_red"] = Button()
        self["key_green"] = Button()
        self["key_yellow"] = Button()
        self["key_blue"] = Button()
        self["ColorActions"] = HelpableActionMap(self, "ColorActions",
        {
            "red": (self.redpressed, ""),
            "green": (self.greenpressed, ""),
            "yellow": (self.yellowpressed, ""),
            "blue": (self.bluepressed, ""),
        })
        self.updateButtonText()
        self.updateHelpText()

    def updateHelpText(self):
        for (actionmap, context, actions) in self.helpList:
            if context == "ColorActions":
                for index, item in enumerate(actions):
                    if item[0] == "red":
                        actions[index] = (item[0], getPluginCaption(config.AdvancedMovieSelection.red.value))
                    if item[0] == "green":
                        actions[index] = (item[0], getPluginCaption(config.AdvancedMovieSelection.green.value))
                    if item[0] == "yellow":
                        actions[index] = (item[0], getPluginCaption(config.AdvancedMovieSelection.yellow.value))
                    if item[0] == "blue":
                        actions[index] = (item[0], getPluginCaption(config.AdvancedMovieSelection.blue.value))

    def updateButtonText(self):
        self["key_red"].setText(getPluginCaption(config.AdvancedMovieSelection.red.value))
        self["key_green"].setText(getPluginCaption(config.AdvancedMovieSelection.green.value))
        self["key_yellow"].setText(getPluginCaption(config.AdvancedMovieSelection.yellow.value))
        self["key_blue"].setText(getPluginCaption(config.AdvancedMovieSelection.blue.value))
        global toggleSeenButton
        if config.AdvancedMovieSelection.red.value == "Toggle seen":
            toggleSeenButton = self["key_red"] 
        elif config.AdvancedMovieSelection.green.value == "Toggle seen":
            toggleSeenButton = self["key_green"] 
        elif config.AdvancedMovieSelection.yellow.value == "Toggle seen":
            toggleSeenButton = self["key_yellow"] 
        elif config.AdvancedMovieSelection.blue.value == "Toggle seen":
            toggleSeenButton = self["key_blue"]
        else:
            toggleSeenButton = None
        
        if toggleSeenButton is not None:
            self.list.connectSelChanged(self.__updateGUI)
        else:
            self.list.disconnectSelChanged(self.__updateGUI)

    def redpressed(self):
        self.startPlugin(config.AdvancedMovieSelection.red.value, self["key_red"])
    
    def greenpressed(self):
        self.startPlugin(config.AdvancedMovieSelection.green.value, self["key_green"])
    
    def yellowpressed(self):
        self.startPlugin(config.AdvancedMovieSelection.yellow.value, self["key_yellow"])
    
    def bluepressed(self):
        self.startPlugin(config.AdvancedMovieSelection.blue.value, self["key_blue"])

    def __updateGUI(self):
        if toggleSeenButton:
            perc = self.list.getMovieStatus()
            if perc > 50:
                toggleSeenButton.setText(_("Mark as unseen"))
            else:
                toggleSeenButton.setText(_("Mark as seen"))
    
    def startPlugin(self, pname, key_number):
        home = config.AdvancedMovieSelection.homepath.value
        bookmark1 = config.AdvancedMovieSelection.bookmark1path.value
        bookmark2 = config.AdvancedMovieSelection.bookmark2path.value
        bookmark3 = config.AdvancedMovieSelection.bookmark3path.value
        errorText = None
        if pname != "Nothing":
            # all functions with no service is needed
            if pname == "Wastebasket":
                if config.AdvancedMovieSelection.use_wastebasket.value:
                    self.session.openWithCallback(self.reloadList, Wastebasket)              
            elif pname == "Home":
                self.gotFilename(home)
            elif pname == "Bookmark 1":
                self.gotFilename(bookmark1)
            elif pname == "Bookmark 2":
                self.gotFilename(bookmark2)
            elif pname == "Bookmark 3":
                self.gotFilename(bookmark3)
            elif pname == "Bookmark(s) on/off":
                if config.AdvancedMovieSelection.show_bookmarks.value:
                    newCaption = _("Show bookmarks")
                else:
                    newCaption = _("Hide bookmarks")
                config.AdvancedMovieSelection.show_bookmarks.value = not config.AdvancedMovieSelection.show_bookmarks.value
                self.saveconfig()
                self.reloadList()
                key_number.setText(newCaption)
            elif pname == "Show/Hide folders":
                if config.AdvancedMovieSelection.showfoldersinmovielist.value:
                    newCaption = _("Show folders")
                else:
                    newCaption = _("Hide folders")
                config.AdvancedMovieSelection.showfoldersinmovielist.value = not config.AdvancedMovieSelection.showfoldersinmovielist.value
                self.showFolders(config.AdvancedMovieSelection.showfoldersinmovielist.value)
                config.AdvancedMovieSelection.showfoldersinmovielist.save()
                self.reloadList()
                key_number.setText(newCaption)
            elif pname == "Sort":
                if config.movielist.moviesort.value == MovieList.SORT_ALPHANUMERIC:
                    newType = MovieList.SORT_DESCRIPTION
                elif config.movielist.moviesort.value == MovieList.SORT_DESCRIPTION:
                    newType = MovieList.SORT_DATE_DESC
                elif config.movielist.moviesort.value == MovieList.SORT_DATE_DESC:
                    newType = MovieList.SORT_DATE_ASC
                elif config.movielist.moviesort.value == MovieList.SORT_DATE_ASC:
                    newType = MovieList.SORT_ALPHANUMERIC
                config.movielist.moviesort.value = newType
                self.setSortType(newType)
                self.reloadList()
                key_number.setText(getPluginCaption(pname))
            elif pname == "Filter by description":
                self.openFilterByDescriptionChoice()
            elif pname == "Show Timer":
                from Screens.TimerEdit import TimerEditList
                self.session.open(TimerEditList)
            else:   
                # all functions that require a service 
                service = self.getCurrent()
                if not service:
                    return
                if pname == "Delete":
                    self.delete()
                elif pname == "Filter by Tags":
                    self.showTagsSelect()
                elif pname == "Tag Editor":
                    if not (service.flags):
                        self.movietags()
                    else:
                        if config.AdvancedMovieSelection.showinfo.value:
                            self.session.open(MessageBox, _("Set tag here not possible, please select a movie for!"), MessageBox.TYPE_INFO)
                elif pname == "Trailer search":
                    if not (service.flags):
                        self.showTrailer()
                    else:
                        if config.AdvancedMovieSelection.showinfo.value:
                            self.session.open(MessageBox, _("Trailer search here not possible, please select a movie!"), MessageBox.TYPE_INFO) 
                elif pname == "Move-Copy":
                    if not (service.flags):
                        self.session.open(MovieMove, self, service)
                    else:
                        if config.AdvancedMovieSelection.showinfo.value:
                            self.session.open(MessageBox, _("Move/Copy from complete directory/symlink not possible, please select a single movie!"), MessageBox.TYPE_INFO)
                elif pname == "Rename":
                    if not (service.flags):
                        self.session.openWithCallback(self.reloadList, MovieRetitle, service)
                    else:
                        if config.AdvancedMovieSelection.showinfo.value:
                            self.session.open(MessageBox, _("Rename here not possible, please select a movie!"), MessageBox.TYPE_INFO)        
                elif pname == "TheTVDB Info & D/L":
                    if not (service.flags):
                        from SearchTVDb import TheTVDBMain
                        self.session.open(TheTVDBMain, service)
                elif pname == "TMDb Info & D/L":
                    if not (service.flags):
                        from SearchTMDb import TMDbMain as TMDbMainsave
                        from ServiceProvider import ServiceCenter
                        searchTitle = ServiceCenter.getInstance().info(service).getName(service)
                        if len(self.list.multiSelection) == 0:
                            self.session.openWithCallback(self.updateCurrentSelection, TMDbMainsave, searchTitle, service)
                        else:
                            from DownloadMovies import DownloadMovies
                            items = []
                            for item in self.list.multiSelection:
                                items.append([item, 0])
                            self.session.openWithCallback(self.updateCurrentSelection, DownloadMovies, items, config.AdvancedMovieSelection.coversize.value)
                    else:
                        if config.AdvancedMovieSelection.showinfo.value:
                            self.session.open(MessageBox, _("TMDb search here not possible, please select a movie!"), MessageBox.TYPE_INFO)               
                elif pname == "Toggle seen":
                    if not (service.flags):
                        perc = self.list.getMovieStatus()
                        if perc > 50:
                            self.setMovieStatus(0)
                            key_number.setText(_("Mark as seen"))
                        else:
                            self.setMovieStatus(1)
                            key_number.setText(_("Mark as unseen"))
                elif pname == "Show up to VSR-X":
                    from AccessRestriction import VSR
                    access = "VSR-%d"%(self.list.getAccess()) 
                    for index, item in enumerate(VSR):
                        if item == access:
                            if len(VSR)-1 == index:
                                access = VSR[0]
                            else:
                                access = VSR[index + 1]
                            break
                    self.list.setAccess(int(access[4:]))
                    self.reloadList()
                    key_number.setText(_("Show up to") + ' ' + _("VSR") + '-%d' % (self.list.getAccess()))
                elif pname == "Mark as seen":
                    if not (service.flags):
                        self.setMovieStatus(status=1)
                    else:
                        if config.AdvancedMovieSelection.showinfo.value:
                            self.session.open(MessageBox, _("This may not be marked as seen!"), MessageBox.TYPE_INFO)
                elif pname == "Mark as unseen":
                    if not (service.flags):
                        self.setMovieStatus(status=0) 
                    else:
                        if config.AdvancedMovieSelection.showinfo.value:
                            self.session.open(MessageBox, _("This may not be marked as unseen!"), MessageBox.TYPE_INFO)
                else:
                    plugin = None
                    for p in plugins.getPlugins(where=[PluginDescriptor.WHERE_MOVIELIST]):
                        if pname == str(p.name):
                            plugin = p
                    if plugin is not None:
                        try:
                            plugin(self.session, service)
                        except:
                            errorText = _("Unknown error!")
                    else: 
                        errorText = _("Plugin not found!")
        else:
            errorText = _("No plugin assigned!")
        if errorText:
            self.session.open(MessageBox, errorText, MessageBox.TYPE_INFO)

    def openAccessChoice(self):
        vsr = []
        vsr.append((_("Clear"), None))        
        vsr.append((_("VSR-0 (General Audience)"), "VSR-0"))        
        vsr.append((_("VSR-6 (Parental Guidance Suggested)"), "VSR-6"))        
        vsr.append((_("VSR-12 (Parents Strongly Cautioned)"), "VSR-12"))        
        vsr.append((_("VSR-16 (Restricted)"), "VSR-16"))        
        vsr.append((_("VSR-18 (No One 17 And Under Admitted)"), "VSR-18"))        
        self.session.openWithCallback(self.setAccessChoice, ChoiceBox, title=_("Please select the VSR here:"), list=vsr)
        
    def setAccessChoice(self, answer):
        if answer:
            answer = answer[1] 
            self.list.setAccessRestriction(answer)
            self.reloadList()

    def openFilterByDescriptionChoice(self):
        from ServiceProvider import ServiceCenter
        from enigma import eServiceReference, iServiceInformation
        from MovieSelection import SHOW_ALL_MOVIES
        serviceHandler = ServiceCenter.getInstance()
        descr = []
        l = serviceHandler.list(self.list.root)
        while 1:
            serviceref = l.getNext()
            if not serviceref.valid():
                break
            if serviceref.flags & eServiceReference.mustDescent:
                continue
            info = serviceHandler.info(serviceref)
            if not info:
                continue
            description = (info.getInfoString(serviceref, iServiceInformation.sDescription),)
            if description[0] != "" and not description in descr: 
                descr.append(description)
        descr = sorted(descr)
        descr.insert(0, (_(SHOW_ALL_MOVIES), ))
        
        current = self.list.filter_description
        selection = 0
        for index, item in enumerate(descr):
            if item[0] == current:
                selection = index
                break
        
        self.session.openWithCallback(self.filterByDescription, ChoiceBox, title=_("Select movie by description:"), list=descr, selection=selection)

    def filterByDescription(self, answer):
        from MovieSelection import SHOW_ALL_MOVIES
        if not answer:
            return
        if answer[0] == _(SHOW_ALL_MOVIES):
            self.list.filter_description = None
        else:
            self.list.filter_description = answer[0] 
        self.reloadList()
