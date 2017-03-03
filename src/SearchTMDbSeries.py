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
from enigma import iServiceInformation
from Source.ServiceProvider import ServiceCenter
from SearchTMDb import TMDbMain
from Source.MovieDB.tmdb import TMDbSeasonInfo, TMDbEpisodeInfo, TMDbSeriesInfo

      
class TMDbSeriesMain(TMDbMain):
#    SHOW_DETAIL_TEXT = _("Show serie detail")
#    SHOW_EPISODE_TEXT = _("Show episode detail")
    SHOW_ALL_EPISODES_TEXT = _("Show episodes overview")
    SHOW_ALL_SEASONS_TEXT = _("Show seasons overview")
    SHOW_ALL_SERIES_TEXT = _("Show search result")
#    MANUAL_SEARCH_TEXT = _("Manual search")
#    INFO_SAVE_TEXT = _("Info/Cover save")
#    TRAILER_SEARCH_TEXT = _("Trailer search")

    def __init__(self, session, service, eventName=None, shortDescription=None):
        TMDbMain.__init__(self, session, eventName, service)
        self['list'].build_update_callback.append(self.__movieUpdate)
#        self.skinName = ["TMDbMain"]
        self.automatic_show_detail = False
        self.searchTitle = eventName
        self.description = shortDescription
        self.selected_serie_index = 0
        self.seasons = []
        self.episodes = []
        if service is not None:
            info = ServiceCenter.getInstance().info(service)
            self.searchTitle = info.getName(service)
            self.description = info.getInfoString(service, iServiceInformation.sDescription)
    
    def __movieUpdate(self, movie):
        if isinstance(movie, TMDbSeasonInfo):
            movie.update()

    def searchForMovies(self):
        try:
            results = TMDbSeriesInfo.search(self.searchTitle)
            if len(results) == 0:
                self.showNoSearchResult()
                return             

            update_seasons = len(results) == 1
            update_episode = len(results) == 1 and self.description
            self.movies = []
            found = (None, -1)
            for serie in results:
                if update_seasons:
                    serie.update()
                self.movies.append((serie,),)
                for season in serie.seasons:
                    #self.movies.append((season, str(season.ID), serie.Title),)
                    if update_episode:
                        season.update()
                    self.movies.append((season, serie.Title),)
                    for episode in season.episodes:
                        if episode.Title == self.description:
                            found = (season, episode.episode_number)
                            self.selected_serie_index = len(self.movies) - 1

            if self.description:
                self.searchTitle = self.searchTitle + " - " + self.description
            if found[0]:
                self.showEpisodeList(found[0], found[1])
            else:
                self.showSeriesList()
        except Exception, e:
            from Source.Globals import printStackTrace
            printStackTrace()
            self["status"].setText(_("Error!\n%s" % e))
            self["status"].show()
            return
    
    def showSeriesList(self):
        self["list"].setList(self.movies)
        self["list"].instance.moveSelectionTo(self.selected_serie_index)
        self.showMovieList()
    
    def showSeasonList(self):
        serie = self.getCurrent()
        if not isinstance(serie, TMDbSeriesInfo):
            serie = serie.serie
        self.seasons = []
        serie.update()
        for season in serie.seasons:
            #self.movies.append((season, str(season.ID), serie.Title),)
            #season.update()
            self.seasons.append((season, serie.Title),)

        self["list"].setList(self.seasons)
        self["list"].instance.moveSelectionTo(0)
        self.showMovieList()
    
    def getEpisodeText(self, episode):
        season_text = str.format("{0} {1}", _("Season:"), episode.season_number)
        episode_text = str.format("{0} {1}", _("Episode:"), episode.episode_number)
        episode_txt = str.format("{0} - {1}", season_text, episode_text)
        return episode_txt

    def showEpisodeList(self, cur=None, episode_number=-1):
        cur = cur or self.getCurrent()
        if not cur or isinstance(cur, TMDbEpisodeInfo):
            self.showMovieList()
            return
        cur.update()
        index = 0
        self.setTitle(str.format("{0} {1}", _("Episodes for:"), self.getInfoText()))
        self.episodes = []
        if isinstance(cur, TMDbSeasonInfo):
            season = cur
            for episode in season.episodes:
                self.episodes.append((episode, self.getEpisodeText(episode)),)
                if episode.Title == self.description:
                    index = len(self.episodes) - 1
                #if episode.episode_number == episode_number:
                #    index = len(self.episodes) - 1
        else:
            serie = cur
            for season in serie.seasons:
                for episode in season.episodes:
                    self.episodes.append((episode, self.getEpisodeText(episode)),)
        self["list"].setList(self.episodes)
        self["list"].instance.moveSelectionTo(index)
        self.showMovieList()
    
    def getInfoText(self):
        if self.description != "" and self.description != self.searchTitle:
            return self.searchTitle + " - " + self.description
        else: 
            return self.searchTitle 

    def updateView(self, mode=None):
        TMDbMain.updateView(self, mode)
        if self.view_mode == self.SHOW_SEARCH or self.view_mode == self.SHOW_SEARCH_NO_RESULT:
            return
        if self["list"].list == self.episodes  or self.view_mode == self.SHOW_MOVIE_DETAIL:
            self["key_red"].setText(self.SHOW_ALL_SERIES_TEXT)
            self["button_red"].show()
        if self["list"].list == self.seasons:
            self["key_red"].setText(self.SHOW_ALL_EPISODES_TEXT)
            self["button_red"].show()
        if self["list"].list == self.movies:
            self["key_red"].setText(self.SHOW_ALL_SEASONS_TEXT)
            self["button_red"].show()

    def ok_pressed(self):
        if self["list"].list == self.movies:
            self.selected_serie_index = self["list"].instance.getCurrentIndex()
        cur = self.getCurrent()
        if isinstance(cur, TMDbSeasonInfo):
            self.showEpisodeList()
        else:
            TMDbMain.ok_pressed(self)

    def buttonAction(self, text):
        if self["list"].list == self.movies:
            self.selected_serie_index = self["list"].instance.getCurrentIndex()
        if text == self.SHOW_ALL_SERIES_TEXT:
            self.showSeriesList()
        elif text == self.SHOW_ALL_SEASONS_TEXT:
            self.showSeasonList()
        elif text == self.SHOW_ALL_EPISODES_TEXT:
            self.showEpisodeList()
        elif text == self.TRAILER_SEARCH_TEXT:
            cur = self.getCurrent()
            if cur:
                title = cur.Title
                if not isinstance(cur, TMDbSeriesInfo):
                    title = cur.serie.Title
                if cur.Title and cur.Title != title:
                    title += " - " + cur.Title
                self.trailerSearch(title)

    def red_pressed(self):
        text = self["key_red"].getText()
        self.buttonAction(text)

    def cancel(self, retval=None):
        if self["list"].list != self.movies or self.view_mode != self.SHOW_RESULT_LIST:
            self.showSeriesList()
        else:
            self.close(False)
