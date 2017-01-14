#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Copyright (C) 2013 cmikula

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

"""An interface to the tmdb3 API"""

config = {}
config['locale'] = 'de'
config['apikey'] = "1f834eb425728133b9a2c1c0c82980eb" # apikey from JD
config['poster_size'] = 'w185'
config['backdrop_size'] = 'w1280'

poster_sizes = ('w92', 'w154', 'w185', 'w342', 'w500', 'original')
backdrop_sizes = ('w300', 'w780', 'w1280', 'original')

def setPosterSize(size):
    value = size.value
    if value in poster_sizes:
        print "[AdvancedMovieSelection] Set tmdb poster size to", value
        config['poster_size'] = value

def setBackdropSize(size):
    value = size.value
    if value in backdrop_sizes:
        print "[AdvancedMovieSelection] Set tmdb backdrop size to", value
        config['backdrop_size'] = value

def setLocale(lng):
    print "[AdvancedMovieSelection] Set tmdb locale to", lng
    config['locale'] = lng

def getLocale():
    return config['locale']

def decodeCertification(releases):
    cert = None
    if releases.has_key('US'):
        cert = releases['US'].certification
    certification = {"G":"VSR-0", "PG":"VSR-6", "PG13":"VSR-12", "PG-13":"VSR-12", "R":"VSR-16", "NC-13":"VSR-18", "NC17":"VSR-18"}
    if certification.has_key(cert):
        return certification[cert]

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

def poster_url(poster, size):
    sizes = poster.sizes()
    if size in sizes:
        return poster.geturl(size)
    p_index = poster_sizes.index(size)
    p_range = range(p_index, len(poster_sizes) - 1)
    for x in p_range:
        size = poster_sizes[x]
        if size in sizes:
            return poster.geturl(size)
    poster.geturl()

def __collect_poster_urls(movie):
    l = []
    if movie.poster is not None:
        l.append(poster_url(movie.poster, config['poster_size']))
    for p in movie.posters:
        url = poster_url(p, config['poster_size'])
        if not url in l:
            l.append(url)
    movie.poster_urls = l
    # print "title: %s, poster: %d" % (movie.title, len(movie.poster_urls))
    movie.poster_index = 1
    if len(movie.poster_urls) > 0:
        movie.poster_url = movie.poster_urls[0]
    else:
        movie.poster_url = None
        movie.poster_index = 0

def __collect_backdrop_urls(movie):
    l = []
    if movie.backdrop is not None:
        l.append(poster_url(movie.backdrop, config['backdrop_size']))
    for p in movie.backdrops:
        url = poster_url(p, config['backdrop_size'])
        if not url in l:
            l.append(url)
    movie.backdrop_urls = l
    # print "title: %s, poster: %d" % (movie.title, len(movie.poster_urls))
    movie.backdrop_index = 1
    if len(movie.backdrop_urls) > 0:
        movie.backdrop_url = movie.backdrop_urls[0]
    else:
        movie.backdrop_url = None
        movie.backdrop_index = 0

def __searchMovie(title, year=None):
    res = original_search(title, year=year)
    for movie in res:
        __collect_poster_urls(movie)
        __collect_backdrop_urls(movie)
    return res

def __searchMovieEx(title, year=None):
    nt = title
    print "__searchMovieEx:", str(nt)
    try:
        import os
        exfile = os.path.dirname(__file__) + '/tmdb.py.txt'
        excludes = []
        with open(exfile,'r') as f:
            for line in f.readlines():
                if line:
                    excludes.append(line.replace('\r', '').replace('\n', '').lower())
    except:
        import sys, traceback
        print "--- [AdvancedMovieSelection] STACK TRACE ---"
        traceback.print_exc(file=sys.stdout)
        print '-' * 50
        excludes = ['german', 'bluray', 'dts', '3d', 'dl', '1080p', '720p', 'x264']
    print excludes

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
    res = original_search(nt, year=year)

    if len(res) == 0:
        tt = nt.split('-')
        if len(tt) > 1:
            res = original_search(tt[0], year=year)
    if len(res) == 0:
        tt = nt.split('&')
        if len(tt) > 1:
            res = original_search(tt[0], year=year)
    if len(res) == 0:
        tt = nt.split(' ')[:-1]
        while len(tt) >= 1 and len(res) == 0:
            tt = " ".join(tt).rstrip()
            res = original_search(tt, year=year)
            tt = tt.split(' ')[:-1]

    for movie in res:
        __collect_poster_urls(movie)
        __collect_backdrop_urls(movie)

    print "__searchMovieEx:", str(len(res))
    return res

import tmdb3
original_search = tmdb3.searchMovie
tmdb3.searchMovie = __searchMovieEx

def init_tmdb3():
    tmdb3.set_key(config['apikey'])
    tmdb3.set_cache('null')
    lng = config['locale']
    if lng == 'en':
        tmdb3.set_locale(lng, 'US')
    elif lng == 'el':
        tmdb3.set_locale(lng, 'GR')
    elif lng == 'cs':
        tmdb3.set_locale(lng, 'CZ')
    elif lng == 'da':
        tmdb3.set_locale(lng, 'DK')
    elif lng == 'uk':
        tmdb3.set_locale('en', 'GB')
    elif lng == 'fy':
        tmdb3.set_locale(lng, 'NL')
    else:
        tmdb3.set_locale(lng, lng.upper())
    print "tmdbv3 locale", tmdb3.get_locale()
    return tmdb3

def main():
    setLocale("de")
    tmdb3 = init_tmdb3()
    res = tmdb3.searchMovie('3D R.I.P.D - Rest in Peace Department')
    res = tmdb3.searchMovie('James Bond 007 - Skyfall')
    res = tmdb3.searchMovie("Bad.Teacher.2011.UNRATED.GERMAN.DTS.DL.720p.BluRay.x264 LeetHD)")
    res = tmdb3.searchMovie('Der.Hobbit.-.Eine.Unerwartete.Reise.(2012).German.DTS.1080p')
    res = tmdb3.searchMovie('Der Hobbit - Eine Unerwartete Reise (2012).German.DTS.1080p.ts')
    # res = tmdb3.searchMovie('Für immer Liebe')
    # res = tmdb3.searchMovie('Fight Club')
    # res = tmdb3.searchMovie('22 Bullets')
    from tmdb3 import Movie
    print Movie(11).poster
    print Movie(11).posters
    print Movie(11).backdrop
    print Movie(11).backdrops
    

    print res
    movie = res[0]
    print movie.title
    print movie.releasedate.year
    print movie.overview
    
    for p in movie.poster_urls:
        print p
    
    for p in movie.posters:
        print p
    for p in movie.backdrops:
        print p
    p = movie.poster
    print p
    print p.sizes()
    print p.geturl()
    print p.geturl('w185')
        
    p = movie.backdrop
    print p
    print p.sizes()
    print p.geturl()
    print p.geturl('w300')
        
    crew = [x.name for x in movie.crew if x.job == 'Director']
    print crew
    crew = [x.name for x in movie.crew if x.job == 'Author']
    print crew
    crew = [x.name for x in movie.crew if x.job == 'Producer']
    print crew
    crew = [x.name for x in movie.crew if x.job == 'Director of Photography']
    print crew
    crew = [x.name for x in movie.crew if x.job == 'Editor']
    print crew
    crew = [x.name for x in movie.crew if x.job == 'Production Design']
    print crew
    cast = [x.name for x in movie.cast]
    print cast
    genres = [x.name for x in movie.genres]
    print genres
    studios = [x.name for x in movie.studios]
    print studios
    countries = [x.name for x in movie.countries]
    print countries

if __name__ == '__main__':
    main()

