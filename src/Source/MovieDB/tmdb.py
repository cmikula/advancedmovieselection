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

from TMDb.tmdbapi import tmdb
from datetime import date
from MovieDBI import MovieDBI
import re
try:
    from ..StopWatch import clockit  # @UnusedImport
except:
    from Source.StopWatch import clockit  # @Reimport

poster_sizes = ('w92', 'w154', 'w185', 'w342', 'w500', 'original')
backdrop_sizes = ('w300', 'w780', 'w1280', 'original')

def setPosterSize(size):
    value = size.value
    if value in poster_sizes:
        print "[AdvancedMovieSelection] Set tmdb poster size to", value
        tmdb.poster_size = value

def setBackdropSize(size):
    value = size.value
    if value in backdrop_sizes:
        print "[AdvancedMovieSelection] Set tmdb backdrop size to", value
        tmdb.backdrop_size = value

def setLocale(lng):
    print "[AdvancedMovieSelection] Set tmdb locale to", lng
    tmdb.language = lng

def getLocale():
    return tmdb.language

def printStackTrace():
    import sys, traceback
    print "--- [AMS:TMDb] STACK TRACE ---"
    traceback.print_exc(file=sys.stdout)
    print '------------------------------'

def search(method, title, year=None):
    try:
        nt = title
        print "TMDb.search:", str(nt)
        excludes = ['.german', '.bluray', '.dts', '.3d', '.dl', '1080p', '720p', 'x264']
    
        if year is None:
            pos1 = nt.find("(")
            pos2 = nt.find(")")
            if pos2 - pos1 == 5:
                year = nt[pos1 + 1:pos2]
                nt = nt[:pos1] + nt[pos2 + 1:]
    
        nt = nt.lower()
        for x in excludes:
            nt = nt.replace(x, '')
        if nt.endswith('.ts'):
            nt = nt[:-3]
    
        nt = nt.replace('.', ' ').rstrip()
        if year is None and title.count('.') > 1:
            match = re.findall('\d{4}', nt)
            if len(match) > 0:
                year = match[-1]
                nt = nt.replace(year, '').rstrip()
        if not nt:
            nt = year
            year = None
        res = method(nt, year)
        
        if len(res) == 0:
            tt = nt.replace('_', ' ').split('-')
            if len(tt) > 1:
                res = method(tt[0], year)
        if len(res) == 0:
            tt = nt.split('-')
            if len(tt) > 1:
                res = method(tt[0], year)
        if len(res) == 0:
            tt = nt.split('&')
            if len(tt) > 1:
                res = method(tt[0], year)
        if len(res) == 0:
            tt = nt.split(' ')[:-1]
            while len(tt) >= 1 and len(res) == 0:
                tt = " ".join(tt).rstrip()
                res = method(tt, year=year)
                tt = tt.split(' ')[:-1]
    
        print "TMDb.search:", str(len(res))
        return res
    except:
        printStackTrace()
        return []


@clockit
def searchMovie(title, year=None):
    res = search(tmdb.searchMovie, title, year)
    result = TMDbMovieInfo.parse(res)
    TMDbBase.sort(result, tmdb.SearchTitle)
    print "TMDb.searchMovie:", str(len(result))
    return result

@clockit
def searchSerie(title):
    res = search(tmdb.searchSerie, title)
    result = TMDbSeriesInfo.parse(res)
    TMDbBase.sort(result, tmdb.SearchTitle)
    print "TMDb.searchSerie:", str(len(result))
    return result

@clockit
def searchSeason(title, season_name):
    res = search(tmdb.searchSerie, title)
    result = TMDbSeriesInfo.parse(res)
    for serie in result:
        serie.update()
        for season in serie.seasons:
            season.update()
            if season.Title == season_name:
                return season

@clockit
def searchEpisode(title, episode_name):
    season_number, episode_number = parseSeasonEpisodeInfo(episode_name)
    if season_number > 0 and episode_number > 0:
        print str.format("[tmdb.searchEpisode] {0} S{1} E{2}", title, season_number, episode_number)
    res = search(tmdb.searchSerie, title)
    result = TMDbSeriesInfo.parse(res)
    for serie in result:
        serie.update()
        if season_number > 0 and episode_number > 0:
            ep = tmdb.getEpisode(serie.ID, season_number, episode_number)
            if ep:
                episode = TMDbEpisodeInfo.parse([ep, ], serie.ID, serie)[0]
                episode.update()
                return episode
            continue
        
        for season in serie.seasons:
            season.update()
            for episode in season.episodes:
                if episode.Title == episode_name:
                    episode.update()
                    return episode

def parseSeasonEpisodeInfo(text):
    if text:
        match = re.findall('S\d+E\d+', text)
        if len(match) == 1:
            s = match[0].split('E')
            S = int(s[0][1:])
            E = int(s[1])
            return S, E
    return 0, 0

class Parser():
    def __init__(self, data, def_str="N/A", def_int=0):
        self.data = data
        self.def_str = def_str
        self.def_int = def_int
    
    def getNumberX(self, key):
        try:
            result = self.data.has_key(key)
            if not result:
                return False, 0
            val = self.data[key]
            if isinstance(val, int):
                return result, int(val)
            if isinstance(val, float):
                return result, float(val)
            if isinstance(val, str):
                return result, str(val)
            return result, self.def_int
        except:
            print self.data
            printStackTrace()
            return False, self.def_int

    def getNumber(self, key):
        return self.getNumberX(key)[1]
        
    def getString(self, key, default=None):
        try:
            return unicode(self.data[key]).encode('utf-8', 'ignore')
        except:
            printStackTrace()
            return default or self.def_str
        
    def getItem(self, key):
        try:
            return self.data[key]
        except:
            printStackTrace()
            return None
    
    def getDate(self, key):
        try:
            datestr = self.getString(key)
            if not datestr:
                return date(1990, 1, 1)
            return date(*[int(x) for x in datestr.split('-')])
        except:
            #printStackTrace()
            return date(1990, 1, 1)
    
    def getPosterUrl(self, key):
        try:
            return tmdb.getPosterUrl(self.data[key])
        except:
            # printStackTrace()
            return None

    def getBackdropUrl(self, key):
        try:
            return tmdb.getBackdropUrl(self.data[key])
        except:
            # printStackTrace()
            return None
        
    def extendList(self, key, ref_list):
        try:
            ref_list.extend(self.data[key])
        except:
            printStackTrace()
            return False

    def getList(self, what, key='name'):
        l = []
        for x in self.data[what]:
            l.append(x[key].encode('utf-8', 'ignore'))
        return l

class TMDbBase(MovieDBI):
    CAST_CHARACTER_FORMAT = "{0} ({1})"
    def __init__(self):
        MovieDBI.__init__(self)
    
    @staticmethod
    def sort(result, search_title):
        print "Sort:", str(search_title)
        # sort per date
        result.sort(key=lambda m: m.ReleaseDate, reverse=True)
        # put 100% result to top
        #result.sort(key=lambda m: m.Title == title, reverse=True)

        def startswith(s, d):
            src = s.lower()
            dst = d.lower()
            if src == dst:
                return 1000
            max_index = min(len(src), len(dst))
            for i in range(0, max_index):
                if src[i] != dst[i]:
                    return i
            return i
        result.sort(key=lambda m: startswith(m.Title, search_title), reverse=True)
        #result.sort(key=lambda m: m.Title.lower() == search_title.lower(), reverse=True)

        for m in result:
            print str.format("{0} {1} {2}", startswith(m.Title, search_title), m.ReleaseDate, m.Title)
    
    def parseCrew(self, results):
        for x in results:
            job = x['job']
            if job == 'Director':
                self.Directors.append(x['name'].encode('utf-8', 'ignore'))
            if job == 'Writer':
                self.Writers.append(x['name'].encode('utf-8', 'ignore'))
            if job == 'Producer':
                self.Producers.append(x['name'].encode('utf-8', 'ignore'))

    def parseCast(self, results, max_cast_id = 0):
        for x in results:
            if max_cast_id > 0 and x['cast_id'] >= self.max_cast_id:
                break
            name = x['name'].encode('utf-8', 'ignore')
            character = x['character'].encode('utf-8', 'ignore')
            self.Cast.append(str.format(self.CAST_CHARACTER_FORMAT, name, character))

    def parseImages(self, res):
        for img in res['images']['posters']:
            f = tmdb.getPosterUrl(img['file_path'])
            if not f in self.poster_urls: 
                self.poster_urls.append(f)
        for img in res['images']['backdrops']:
            f = tmdb.getBackdropUrl(img['file_path'])
            if not f in self.backdrop_urls:
                self.backdrop_urls.append(f)
        
        if len(self.poster_urls) > 0:
            self.poster_index = 1
        if len(self.backdrop_urls) > 0:
            self.backdrop_index = 1


class TMDbMovieInfo(TMDbBase):
    def __init__(self):
        TMDbBase.__init__(self)
        self.language = tmdb.language
        self.max_cast_id = 10

    @staticmethod
    def search(title, year=None):
        result = searchMovie(title, year)
        return result
            
    @staticmethod
    def parse(res):
        result = []
        for movie in res:
            p = Parser(movie)
            dbi = TMDbMovieInfo()
            dbi.ID = p.getNumber('id')
    
            dbi.Title = p.getString('title')
            dbi.Overview = p.getString('overview')
    
            dbi.ReleaseDate = p.getDate('release_date')
            dbi.Votes = p.getNumber('vote_count')
            dbi.UserRating = p.getNumber('vote_average')
            dbi.Popularity = p.getNumber('popularity')
    
            dbi.poster_url = p.getPosterUrl('poster_path')
            dbi.backdrop_url = p.getBackdropUrl('backdrop_path')
    
            result.append(dbi)
    
        return result

    def update(self):
        print self.__class__.__name__ + ".update()"
        if self.full_loaded:
            return
        res = tmdb.getMovie(self.ID)
        if res is not None:
            p = Parser(res)
            # dbi = MovieDBI()
            self.init()
            self.full_loaded = True
            self.ID = p.getNumber('id')
    
            self.Title = p.getString('title')
            self.Overview = p.getString('overview')
    
            self.ReleaseDate = p.getDate('release_date')
            self.Votes = p.getNumber('vote_count')
            self.UserRating = p.getNumber('vote_average')
            self.Popularity = p.getNumber('popularity')
    
            self.poster_url = p.getPosterUrl('poster_path')
            if self.poster_url:
                self.poster_urls.append(self.poster_url)
            self.backdrop_url = p.getBackdropUrl('backdrop_path')
            if self.backdrop_url:
                self.backdrop_urls.append(self.backdrop_url)
            
            self.Runtime = p.getNumber('runtime')
            self.Genres = p.getList('genres')
            self.Studios = p.getList('production_companies')
            self.Countries = p.getList('production_countries')
            self.CountriesShort = p.getList('production_countries', 'iso_3166_1')
            
            self.parseImages(res)
            
            self.parseCast(res['casts']['cast'], self.max_cast_id)
            self.parseCrew(res['casts']['crew'])
            
            self.decodeCertification(res['release_dates'])
            return self

    def decodeCertification(self, releases):
        certification = \
        {
            "US" : {"G":"0", "PG":"6", "PG13":"12", "PG-13":"12", "R":"16", "NC-13":"18", "NC17":"18"},
            "DE" : {"0":"0", "6":"6", "12":"12", "16":"16", "18":"18"},
        }
        results = releases['results']
        for key, value in certification.iteritems():
            for rel in results:
                cert = rel['release_dates'][0]['certification']
                if rel['iso_3166_1'] == key and value.has_key(cert):
                    code = value[cert]
                    self.Certification = "VSR-" + code
                    return


def __nextIndex(idx, l):
    return idx + 1 if idx < len(l) else 1

def __prevIndex(idx, l):
    return idx - 1 if idx > 1 else len(l)

def nextImageIndex(movie):
    if len(movie.poster_urls) == 0:
        return
    movie.poster_index = __nextIndex(movie.poster_index, movie.poster_urls)
    if len(movie.poster_urls) > 1:
        item = movie.poster_urls.pop(0)
        movie.poster_urls.append(item)
    movie.poster_url = movie.poster_urls[0]

def prevImageIndex(movie):
    if len(movie.poster_urls) == 0:
        return
    movie.poster_index = __prevIndex(movie.poster_index, movie.poster_urls)
    if len(movie.poster_urls) > 1:
        item = movie.poster_urls.pop(-1)
        movie.poster_urls.insert(0, item)
    movie.poster_url = movie.poster_urls[0]

def nextBackdrop(movie):
    if len(movie.backdrop_urls) == 0:
        return
    movie.backdrop_index = __nextIndex(movie.backdrop_index, movie.backdrop_urls)
    if len(movie.backdrop_urls) > 1:
        item = movie.backdrop_urls.pop(0)
        movie.backdrop_urls.append(item)
    movie.backdrop_url = movie.backdrop_urls[0]

def prevBackdrop(movie):
    if len(movie.backdrop_urls) == 0:
        return
    movie.backdrop_index = __prevIndex(movie.backdrop_index, movie.backdrop_urls)
    if len(movie.backdrop_urls) > 1:
        item = movie.backdrop_urls.pop(-1)
        movie.backdrop_urls.insert(0, item)
    movie.backdrop_url = movie.backdrop_urls[0]

class TMDbSeriesInfo(TMDbBase):
    def __init__(self):
        TMDbBase.__init__(self)
        self.language = tmdb.language
        self.seasons = []
        self.serie_id = 0
    
    @staticmethod
    def search(title):
        result = searchSerie(title)
        return result

    @staticmethod
    def parse(res):
        result = []
        for movie in res:
            p = Parser(movie)
            dbi = TMDbSeriesInfo()
            dbi.serie_id = dbi.ID = p.getNumber('id')
    
            dbi.Title = p.getString('name')
            dbi.Overview = p.getString('overview')
    
            dbi.ReleaseDate = p.getDate('first_air_date')
            dbi.Votes = p.getNumber('vote_count')
            dbi.UserRating = p.getNumber('vote_average')
            dbi.Popularity = p.getNumber('popularity')
    
            dbi.poster_url = p.getPosterUrl('poster_path')
            dbi.backdrop_url = p.getBackdropUrl('backdrop_path')
    
            result.append(dbi)
    
        return result
    
    def update(self):
        print self.__class__.__name__ + ".update()"
        if self.full_loaded:
            return
        res = tmdb.getSerie(self.ID)

        p = Parser(res)

        self.init()
        self.full_loaded = True
        self.ID = p.getNumber('id')
        self.seasons = TMDbSeasonInfo.parse(res['seasons'], self.serie_id, self)

        self.Title = p.getString('name')
        self.Overview = p.getString('overview')

        self.ReleaseDate = p.getDate('first_air_date')
        self.Votes = p.getNumber('vote_count')
        self.UserRating = p.getNumber('vote_average')
        self.Popularity = p.getNumber('popularity')

        self.poster_url = p.getPosterUrl('poster_path')
        if self.poster_url:
            self.poster_urls.append(self.poster_url)
        self.backdrop_url = p.getBackdropUrl('backdrop_path')
        if self.backdrop_url:
            self.backdrop_urls.append(self.backdrop_url)
        
        if len(res['episode_run_time']) > 0:
            self.Runtime = int(res['episode_run_time'][0])

        self.Genres = p.getList('genres')
        self.Studios = p.getList('production_companies')

        self.parseImages(res)
        
        for x in res['origin_country']:
            self.CountriesShort.append(x.encode('utf-8', 'ignore'))

        self.parseCast(res['credits']['cast'])
        self.parseCrew(res['credits']['crew'])

        return self

class TMDbSeasonInfo(TMDbBase):
    def __init__(self):
        TMDbBase.__init__(self)
        self.language = tmdb.language
        self.serie = None
        self.season_number = 0
        self.episodes = []
    
    @staticmethod
    def parse(res, serie_id, serie):
        result = []
        for movie in res:
            p = Parser(movie)
            dbi = TMDbSeasonInfo()
            dbi.serie = serie
            dbi.ID = p.getNumber('id')
            dbi.serie_id = serie_id
            dbi.season_number = p.getNumber('season_number')
            dbi.poster_url = p.getPosterUrl('poster_path')
            result.append(dbi)
        return result
    
    def update(self):
        print self.__class__.__name__ + ".update()"
        if self.full_loaded:
            return
        res = tmdb.getSeason(self.serie_id, self.season_number)
        p = Parser(res)
        self.init()
        self.full_loaded = True
        self.ID = p.getNumber('id')
        self.episodes = TMDbEpisodeInfo.parse(res['episodes'], self.serie_id, self.serie)

        self.Title = p.getString('name')
        self.Overview = p.getString('overview')

        self.ReleaseDate = p.getDate('air_date')
        self.poster_url = p.getPosterUrl('poster_path')
        if self.poster_url:
            self.poster_urls.append(self.poster_url)
        if len(self.poster_urls) > 0:
            self.poster_index = 1
        return self

   

class TMDbEpisodeInfo(TMDbBase):
    def __init__(self):
        TMDbBase.__init__(self)
        self.language = tmdb.language
        self.serie = None
        self.season_number = 0
        self.episode_number = 0
    
    @staticmethod
    def parse(res, serie_id, serie):
        result = []
        for movie in res:
            p = Parser(movie)
            dbi = TMDbEpisodeInfo()
            dbi.serie_id = serie_id
            dbi.serie = serie
            dbi.ID = p.getNumber('id')
            dbi.season_number = p.getNumber('season_number')
            dbi.episode_number = p.getNumber('episode_number')
    
            dbi.Title = p.getString('name')
            dbi.Overview = p.getString('overview')
    
            dbi.ReleaseDate = p.getDate('air_date')
            dbi.Votes = p.getNumber('vote_count')
            dbi.UserRating = p.getNumber('vote_average')
            dbi.Popularity = p.getNumber('popularity')
    
            dbi.poster_url = p.getPosterUrl('still_path')

            result.append(dbi)
    
        return result
    
    def update(self):
        print self.__class__.__name__ + ".update()"
        if self.full_loaded:
            return
        res = tmdb.getEpisode(self.serie_id, self.season_number, self.episode_number)
        p = Parser(res)
        # dbi = MovieDBI()
        self.init()
        self.full_loaded = True
        self.ID = p.getNumber('id')

        self.Title = p.getString('name')
        self.Overview = p.getString('overview')

        self.ReleaseDate = p.getDate('air_date')
        self.Votes = p.getNumber('vote_count')
        self.UserRating = p.getNumber('vote_average')

        self.poster_url = p.getPosterUrl('still_path')
        if self.poster_url:
            self.poster_urls.append(self.poster_url)

        for img in res['images']['stills']:
            f = tmdb.getBackdropUrl(img['file_path'])
            if not f in self.backdrop_urls:
                self.backdrop_urls.append(f)
        
        if len(self.poster_urls) > 0:
            self.poster_index = 1
        if len(self.backdrop_urls) > 0:
            self.backdrop_index = 1
            self.backdrop_url = self.backdrop_urls[0]
        
        self.parseCast(res['credits']['cast'])
        self.parseCrew(res['credits']['crew'])

        if self.serie is not None:
            self.setSerieInfo(self.serie)

        return self
    
    def setSerieInfo(self, serie):
        self.CountriesShort = serie.CountriesShort
        self.Genres = serie.Genres
        self.Studios = serie.Studios
        self.Runtime = serie.Runtime
        # self.Cast = serie.Cast
        # self.Directors = serie.Directors
        # self.Writers = serie.Writers
        # self.Producers = serie.Producers

def main():
    if True:
        episode = searchEpisode('Castle', 'S08E14 Der Club der Meisterdetektive') 
        series = searchSerie('Blindspot')
        serie = series[0]
        serie.update()
        season = serie.seasons[1]
        season.update()
        episode = season.episodes[2]
        episode.update()
        season = searchSeason('Blindspot', 'Staffel 2')
        episode = searchEpisode('Blindspot', 'Eingeschlossen')
        info = searchEpisode('Blindspot', 'Eingeschlossen')
        info = searchEpisode('The Last Ship', 'Casus Belli') # 'The Last Ship', 'Casus Belli' S05E01
        print info
        series = TMDbSeriesInfo.search('Blindspot')
        #series = TMDbSeriesInfo.search('Law & Order')
        #series = TMDbSeriesInfo.search('2_Broke_Girls_-_S06E04_-_Taufman')
        serie = series[0].update()
        for season in serie.seasons:
            season.update()
            print season.Title
            for episode in season.episodes:
                #episode.update()
                print episode.Title

    res = searchMovie('Die Verschwörung - Tödliche Geschäfte')
    from __init__ import downloadCover
    downloadCover(res[0].backdrop_url, "test.png", True)
    res = res[0].update()
    res = searchMovie('2012.2009.German.DL.1080p.BluRay')
    res = res[0].update()
    res = searchMovie('Conan.2011.German.1080p')
    res = searchMovie('300')
    res = searchMovie('3D R.I.P.D - Rest in Peace Department')
    res = searchMovie('James Bond 007 - Skyfall')
    res = searchMovie("Bad.Teacher.2011.UNRATED.GERMAN.DTS.DL.720p.BluRay.x264 LeetHD)")
    res = searchMovie('Der.Hobbit.-.Eine.Unerwartete.Reise.(2012).German.DTS.1080p')
    res = searchMovie('Der Hobbit - Eine Unerwartete Reise (2012).German.DTS.1080p.ts')

if __name__ == '__main__':
    main()

