#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Copyright (C) 2017 cmikula

In case of reuse of this source code please do not remove this copyright.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    For more information on the GNU General Public License see:
    <http://www.gnu.org/licenses/>.

For example, if you distribute copies of such a program, whether gratis or for a fee, you 
must pass on to the recipients the same freedoms that you received. You must make sure 
that they, too, receive or can get the source code. And you must show them these terms so they know their rights.
'''

from datetime import date

class MovieDBI():
    def __init__(self):
        self.init()
        self.language = "de"
    
    def init(self):
        self.full_loaded = False
        self.ID = 0
        self.Title = ""
        self.Overview = ""
        self.Certification = ""
        self.Runtime = 0
        
        self.ReleaseDate = date(1900, 01, 01)
        self.AlternateTitle = ""
    
        self.Genres = []
        self.Cast = []
        self.Crew = []
        #self.Actors = []
        self.Writers = []
        self.Directors = []
        self.Producers = []
        self.Studios = []
        self.Countries = []
        self.CountriesShort = []
        
        self.Votes = 0
        self.UserRating = 0.0
        self.Popularity = 0.0
        #self.FirstAired = 0
        
        self.poster_url = None
        self.backdrop_url = None
        self.poster_index = 0
        self.backdrop_index = 0
        self.poster_urls = []
        self.backdrop_urls = []
    
    def update(self):
        pass
    
    def getLocale(self):
        return self.language
