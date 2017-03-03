#!/usr/bin/python
# -*- coding: utf-8 -*-
#  Netatmo for Dreambox-Enigma2
#
#  Coded by cmikula (c)2017
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

from urllib import urlencode
import base64

REQUESTS = False
try:
    import requests
    REQUESTS = True
except:
    import json
    import urllib2


CONNECTION_TIMEOUT = 20
API_KEY = 'MWY4MzRlYjQyNTcyODEzM2I5YTJjMWMwYzgyOTgwZWI='

_BASE_URL = "http://api.themoviedb.org/3/"
_SEARCH_MOVIE = _BASE_URL + "search/movie"
_GET_MOVIE = _BASE_URL + "movie/"
_BASE_IMAGE_URL = "http://image.tmdb.org/t/p/"
_SEARCH_SERIE = _BASE_URL + "search/tv"
_GET_SERIE = _BASE_URL + "tv/{0}"
_GET_SEASON = _BASE_URL + "tv/{0}/season/{1}"
_GET_EPISODE = _BASE_URL + "tv/{0}/season/{1}/episode/{2}"

class TMDb():
    def __init__(self):
        self.api_key = base64.b64decode(API_KEY)
        self.language = 'de'
        self.language_fallback = 'en'
        self.adult = False
        self.poster_size = 'w185'
        self.backdrop_size = 'w1280'
        self.SearchTitle = ""

    def getPosterUrl(self, file_path):
        return _BASE_IMAGE_URL + self.poster_size + file_path
        
    def getBackdropUrl(self, file_path):
        return _BASE_IMAGE_URL + self.backdrop_size + file_path
        
    def searchMovie(self, query, year=None):
        self.SearchTitle = query
        args = {
            'api_key': self.api_key,
            'language': self.language,
            'query': query,
            'include_adult': self.adult and 'true' or 'false',
            }
        if year is not None:
            try:
                args['year'] = year.year
            except AttributeError:
                args['year'] = year
        resp = self.__getJson(_SEARCH_MOVIE, args)
        return resp['results']
    
    def getMovie(self, movieid):
        args = {
            'api_key': self.api_key,
            'language': self.language,
            'append_to_response': 'images,casts,release_dates',
            'include_image_language': str.format('{0},{1}', self.language, self.language_fallback)
            }
        resp = self.__getJson(_GET_MOVIE + str(movieid), args)
        return resp

    def searchSerie(self, query, year=None):
        self.SearchTitle = query
        args = {
            'api_key': self.api_key,
            'language': self.language,
            'query': query,
            'include_adult': self.adult and 'true' or 'false',
            }
        if year is not None:
            try:
                args['year'] = year.year
            except AttributeError:
                args['year'] = year
        resp = self.__getJson(_SEARCH_SERIE, args)
        return resp['results']
    
    def getSerie(self, serie_id):
        args = {
            'api_key': self.api_key,
            'language': self.language,
            'append_to_response': 'images,credits,release_dates',
            'include_image_language': str.format('{0},{1}', self.language, self.language_fallback)
            }
        url = str.format(_GET_SERIE, serie_id) 
        resp = self.__getJson(url, args)
        return resp

    def getSeason(self, serie_id, season_number):
        args = {
            'api_key': self.api_key,
            'language': self.language,
            'append_to_response': 'images,credits,release_dates',
            'include_image_language': str.format('{0},{1}', self.language, self.language_fallback)
            }
        url = str.format(_GET_SEASON, serie_id, season_number) 
        resp = self.__getJson(url, args)
        return resp

    def getEpisode(self, serie_id, season_number, episode_number):
        args = {
            'api_key': self.api_key,
            'language': self.language,
            'append_to_response': 'images,credits,release_dates',
            'include_image_language': str.format('{0},{1}', self.language, self.language_fallback)
            }
        url = str.format(_GET_EPISODE, serie_id, season_number, episode_number) 
        resp = self.__getJson(url, args)
        return resp

    def __getJson(self, url, params):
        if REQUESTS:
            params = urlencode(params)
            r = requests.get(url, params, timeout=CONNECTION_TIMEOUT)
            j = r.json()
            #print j
            return j
        else:
            params = urlencode(params)
            headers = {"Content-Type" : "application/json;charset=utf-8"}
            req = urllib2.Request(url=url + '?' + params, headers=headers)
            resp = urllib2.urlopen(req).read()
            j = json.loads(resp)
            #print j
            return j

tmdb = TMDb()


if __name__ == "__main__":
    res = tmdb.searchSerie('Blindspot')[0]
    serie = tmdb.getSerie(res)
    season = tmdb.getSeason(serie, serie['seasons'][0]['season_number'])
    episode = tmdb.getEpisode(serie, serie['seasons'][0]['season_number'], season['episodes'][0]['episode_number'])
    res = tmdb.searchMovie('2012', '2009')
    res = tmdb.getMovie(res[0]['id'])
    print res
    
    
    
    
    
