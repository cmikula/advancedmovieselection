#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Copyright (C) 2011 cmikula

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

DVB transports include metadata called Service Information (DVB-SI, ETSI EN 300 468, ETSI TR 101 211) 
that links the various elementary streams into coherent programs and provides human-readable descriptions 
for electronic program guides as well as for automatic searching and filtering.

Based on: en_300468v010901p.pdf
Digital Video Broadcasting (DVB) Specification for Service Information (SI) in DVB systems
'''

import os, time
from EventInformationTable import EventInformationTable, writeEIT, getLanguageCode, printStackTrace
from MovieDB import tmdb, tvdb, downloadCover
from MovieDB.MovieDBI import MovieDBI


def appendShortDescriptionToMeta(file_name, short_descr):
    try:
        meta_file = file_name.endswith(".ts") and file_name + ".meta" or file_name + ".ts.meta"  
        if os.path.exists(meta_file):
            metafile = open(meta_file, "r")
            sid = metafile.readline()
            title = metafile.readline().rstrip()
            descr = metafile.readline().rstrip()
            rest = metafile.read()
            metafile.close()
            if descr != "":
                print "Update metafile skipped"
                return
            print "Update metafile: ", meta_file
            descr = short_descr
            metafile = open(meta_file, "w")
            metafile.write("%s%s\n%s\n%s" % (sid, title, descr, rest))
            metafile.close()
    except Exception, e:
        print e

def setTmdbCertificationtion(movie, file_name):
    try:
        cert = movie.Certification
        if cert:
            from AccessRestriction import accessRestriction
            accessRestriction.setToService(file_name, cert)
    except Exception, e:
        print e

class OverwriteSettings:
    def __init__(self):
        self.eit = False
        self.cover = False
        self.backdrop = False

def writeEITex(file_name, movie=MovieDBI(), overwrite=OverwriteSettings()):
    try:
        # DVD directory
        if not os.path.isdir(file_name):
            f_name = os.path.splitext(file_name)[0]
        else:
            f_name = file_name
        eit_file = f_name + ".eit"
        jpg_file = f_name + ".jpg"
        backdrop_file = f_name + ".backdrop.jpg"
        
        # check and cancel if all exists
        if (not overwrite.eit and os.path.exists(eit_file)) and \
        (not overwrite.cover and os.path.exists(jpg_file)) and \
        (not overwrite.backdrop and os.path.exists(backdrop_file)):
            print "Cancel all data exists:", str(file_name)
            return
        
        movie.update()
        name = movie.Title
        overview = movie.Overview
        runtime = movie.Runtime
        genre = " ".join(movie.Genres)
        directors = movie.Directors
        writers = movie.Writers
        producers = movie.Producers
        actors = movie.Cast
        released = movie.ReleaseDate
        countries = movie.CountriesShort

        # update certificate and meta genre
        appendShortDescriptionToMeta(file_name, genre)
        setTmdbCertificationtion(movie, file_name)
        
        downloadCover(movie.poster_url, jpg_file, overwrite.cover)
        downloadCover(movie.backdrop_url, backdrop_file, overwrite.backdrop)

        if os.path.exists(eit_file) and overwrite.eit == False:
            print "File '%s' already exists, eit creation skipped!" % (eit_file)
            return True 

        # Checking valid movie name
        if not name or len(name) == 0:
            print "tmdb search results no valid movie name"
            return False
        # Checking valid movie overview
        if not overview or len(overview) == 0:
            print "tmdb search results no valid movie overview"
            return False

        ex_info = []
        print countries
        country = ", ".join(countries)
        print country
        country = country.replace("US", "USA").replace("DE", "GER")
        if released:
            country += " " + str(released.year)
            country = country.lstrip()
        print country
        ex_info.append(country) 
        print ex_info

        if runtime:
            ex_info.append(str.format("{0} Min", runtime)) 
        
        if len(directors) > 0:
            ex_info.append("Von " + ", ".join(directors))
        elif len(writers) > 0:
            ex_info.append("Von " + ", ".join(writers))
        elif len(producers) > 0:
            ex_info.append("Von " + ", ".join(producers))
        
        if len(actors) > 0:
            ex_info.append("Mit " + ", ".join(actors))
        extended_info = ". ".join(ex_info)
        print "Overview:"
        print " " * 4, overview
        print "Extended info:"
        print " " * 4, extended_info
        
        language_code = "DEU"
        if movie.language == "ru":
            language_code = "rus"

        return writeEIT(file_name, eit_file, name, overview, genre, extended_info, str(released), runtime, language_code)
    except:
        printStackTrace()
        return False

def eitFromTMDb(file_name, title, overwrite=OverwriteSettings()):
    try:
        results = tmdb.searchMovie(title)
        if len(results) > 0:
            movie = results[0]
            writeEITex(file_name, movie, overwrite)
    except:
        printStackTrace()

def downloadTMDbSerie(file_name, title, overwrite=OverwriteSettings()):
    try:
        results = tmdb.searchSerie(title)
        if len(results) > 0:
            movie = results[0]
            writeEITex(file_name, movie, overwrite)
    except:
        printStackTrace()

        
def createEITtvdb(file_name, title, serie=None, episode=None, overwrite_eit=False, overwrite_cover=False, overwrite_backdrop=False, cover_type='poster', backdrop_type='fanart'):
    try:
        # DVD directory
        if not os.path.isdir(file_name):
            f_name = os.path.splitext(file_name)[0]
        else:
            f_name = file_name
        eit_file = f_name + ".eit"
        jpg_file = f_name + ".jpg"
        backdrop_file = f_name + ".backdrop.jpg"
        
        if serie == None and title:
            print "Fetching info for movie: " + str(title)
            results = tvdb.search(title)
            if len(results) == 0:
                print "No info found for: " + str(title)
                return False
            searchResult = results[0]
            movie = tvdb.getMovieInfo(searchResult['id'])
            serie = movie['Serie'][0]
        
        cover_url = serie[cover_type]
        backdrop_url = serie[backdrop_type]
        downloadCover(cover_url, jpg_file, overwrite_cover)
        downloadCover(backdrop_url, backdrop_file, overwrite_backdrop)

        if os.path.exists(eit_file) and overwrite_eit == False:
            print "File '%s' already exists, eit creation skipped!" % (eit_file)
            return True 

        name = serie['SeriesName']
        overview = serie['Overview']
        print "Series title:", str(name)
        # Checking valid movie name
        if not name or len(name) == 0:
            print "tvdb search results no valid movie name"
            return False
        # Checking valid movie overview
        if not overview or len(overview) == 0:
            print "tvdb search results no valid movie overview"
            return False

        runtime = serie['Runtime']
        genre = ""
        if serie['Genre']:
            genre = " ".join(serie['Genre'])

        directors = None
        actors = None
        if serie['Actors']:
            actors = serie['Actors']
            
        released = None
        if serie['FirstAired']:
            released = serie['FirstAired']     

        if episode:
            episode_name = episode['EpisodeName'] 
            if episode_name:
                name = name + " - " + episode_name
            episode_overview = episode['Overview']
            if episode_overview:
                overview = episode_overview
            if episode['FirstAired']:
                released = episode['FirstAired']     
            if episode.has_key('Director') and episode['Director']:
                directors = episode['Director']     

        ex_info = []
        if released:
            try:
                year = released[0:4]
                ex_info.append(year) 
            except Exception, e:
                print e

        if runtime:
            try:
                rt = str(int(runtime))
                ex_info.append(rt + " Min") 
            except Exception, e:
                print e
        
        if directors:
            ex_info.append("Von " + ", ".join(directors))
        if actors:
            ex_info.append("Mit " + ", ".join(actors))
        extended_info = ". ".join(ex_info)
        print "Extended info:"
        print " " * 4, extended_info

        language_code = getLanguageCode(tvdb)
        return writeEIT(file_name, eit_file, name, overview, genre, extended_info, released, runtime, language_code)
    except:
        printStackTrace()
        return False


# Debug only 
def detectDVDStructure(loadPath):
    if not os.path.isdir(loadPath):
        return None
    if os.path.exists(loadPath + "VIDEO_TS.IFO"):
        return loadPath + "VIDEO_TS.IFO"
    if os.path.exists(loadPath + "VIDEO_TS/VIDEO_TS.IFO"):
        return loadPath + "VIDEO_TS/VIDEO_TS.IFO"
    return None

class eServiceReference():
    def __init__(self, dummy_self, _file=None):
        if _file == None:
            _file = dummy_self
        self.file = str(_file).split("4097:0:0:0:0:0:0:0:0:0:")[1]
        self.name = os.path.basename(self.file).rsplit(".")[0]
        if os.path.isdir(self.file) and self.file[-1] != '/':
            self.file += "/"
            
    def getPath(self):
        return self.file

    def setPath(self, path):
        self.file = path

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

class eServiceReferenceDvd(eServiceReference):
    def __init__(self, serviceref, dvdStruct=False):
        eServiceReference.__init__(self, "4097:0:0:0:0:0:0:0:0:0:" + serviceref.getPath())
        self.dvdStruct = dvdStruct
        if dvdStruct is True:
            # remove trailing slash
            self.setPath(self.getPath()[0:-1])

        self.setName(os.path.basename(os.path.splitext(serviceref.getPath())[0]))
            
    def getDVD(self):
        if self.dvdStruct is True:
            return [self.getPath() + "/"]
        else:
            return [self.getPath()]

def checkCreateMetaFile(ref):
    _file = ref.getPath() + ".ts.meta"
    if not os.path.exists(_file):
        if os.path.isfile(ref.getPath()):
            title = os.path.basename(os.path.splitext(ref.getPath())[0])
        else:
            title = ref.getName()
        sid = ""
        descr = ""
        time = ""
        tags = ""
        metafile = open(_file, "w")
        metafile.write("%s\r\n%s\r\n%s\r\n%s\r\n%s" % (sid, title, descr, time, tags))
        metafile.close()

class ServiceInfo:
    def __init__(self, serviceref):
        self.servicename = ""
        self.description = ""
        self.tags = ""
        try:
            try:
                checkCreateMetaFile(serviceref)
            except Exception, e:
                print e
                if os.path.isfile(serviceref.getPath()):
                    self.name = os.path.basename(serviceref.getPath()).split('.')[0]
                else:
                    self.name = serviceref.getName()
                return
            if os.path.exists(serviceref.getPath() + ".ts.meta"):
                _file = open(serviceref.getPath() + ".ts.meta", "r")
                _file.readline()
                self.name = _file.readline().rstrip("\r\n")
                self.description = _file.readline().rstrip("\r\n")
                _file.readline()
                self.tags = _file.readline().rstrip("\r\n")
                _file.close()
        except Exception, e:
            print "Exception in load meta data: " + str(e)

    def getServiceName(self):
        return self.servicename

    def getName(self):
        return self.name

    def getDescription(self):
        return self.description

    def getTags(self):
        return self.tags

# ~ Debug only

def printEIT(file_name):    
    print "\nEIT info for: " + file_name
    eit = EventInformationTable(file_name)
    print "ID:0x%04X %s %s" % (eit.event_id, eit.start_time, eit.duration)
    print eit.getEventName()
    print eit.getEventId()
    print eit.getShortDescription()
    print eit.getExtendedDescription()
    print eit.getBeginTimeString()
    print eit.getBeginTime()
    print eit.getDuration() / 60
    print "Length: " + str(eit.descriptors_loop_length)
    print "\n"

def compareResult(org, ref):
    if isinstance(ref, str):
        if org != ref:
            raise Exception("data not match")
    if isinstance(ref, list):
        for r in ref:
            if org != r:
                raise Exception("data not match")

def testEIT(language_code, TEST_STRING):
    print TEST_STRING
    file_name = "/tmp/eit_test.mkv"
    eit_file = "/tmp/eit_test.eit"
    name = TEST_STRING
    overview = TEST_STRING
    genre = TEST_STRING
    extended_info = TEST_STRING
    released = "2012.10.31"
    runtime = 90
    writeEIT(file_name, eit_file, name, overview, genre, extended_info, released, runtime, language_code)
    
    eit = EventInformationTable(eit_file)
    compareResult(TEST_STRING, eit.getEventName())
    compareResult(TEST_STRING, eit.getShortDescription())
    compareResult(TEST_STRING, eit.getExtendedDescription().split("\n"))
    if eit.getDuration() != 90 * 60:
        raise Exception("data not match")
    tuple1 = eit.getBeginTimeString().split(' ')[0].split(".")
    tuple2 = released.split(".")
    tuple2.reverse()
    if tuple1 != tuple2:  
        raise Exception("data not match")

def testMultiEit():
    TEST_RUS1 = "АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя"
    TEST_RUS2 = "0123456789 abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ @ -^!\"§$%&/()=?+-/*~#'_.:,;<>|`{[]}"
    TEST_DEU = "0123456789 abcdefghijklmnopqrstuvwxyz äöüß ABCDEFGHIJKLMNOPQRSTUVWXYZ ÄÖÜ@€ -^°!\"§$%&/()=?+-/*~#'_.:,;<>|´`{[]}"
    testEIT("DEU", TEST_DEU)
    testEIT("rus", TEST_RUS1)
    testEIT("rus", TEST_RUS2)

if __name__ == '__main__':
    testMultiEit()
    downloadTMDbSerie("/tmp/Blindspot_tmdb.ts", "Blindspot")
    createEITtvdb("/tmp/Blindspot_tvdb.ts", "Blindspot")
    eitFromTMDb("/tmp/2012_test.ts", "2012 (2009)")
    results = tmdb.searchMovie("2012", "2009")
    movie = results[0].update()
    overwrite = OverwriteSettings()
    overwrite.eit = True
    overwrite.cover = True
    overwrite.backdrop = True
    writeEITex("/tmp/2012_test.ts", movie, overwrite)
    
    tmdb.setLocale('de')
    eitFromTMDb("/tmp/Fight Club.ts", "Fight Club", overwrite)
    tmdb.setLocale('ru')
    eitFromTMDb("/tmp/Blitz_ru.ts", "Черная Молния", overwrite)
    tmdb.setLocale('de')
    printEIT("/tmp/Blitz_ru.eit")
    printEIT("/tmp/russia.eit")
    printEIT("/tmp/Shutter Island ru Original.eit")
    printEIT("/tmp/Shutter Island ru tmdb.eit")

    printEIT("/tmp/22 Bullets.eit")

    results = tvdb.search("Law & Order")
    #results = search("The Mentalist")
    for searchResult in results:
        movie = tvdb.getMovieInfo(searchResult['id'])
        serie = movie['Serie'][0]
        episode = tvdb.searchEpisode(movie['Episode'], "Die Wunderdoktorin")
        if episode:
            createEITtvdb("/tmp/Law & Order.ts", None, overwrite_eit=True, serie=serie, episode=episode)
    
    path = "/tmp/"
    supported = ["ts", "iso", "mkv"]
    dirList = os.listdir(path)
    printEIT("/tmp/22 Bullets.eit")
    eitFromTMDb("/tmp/22 Bullets.ts", "22 Bullets", overwrite)
    createEITtvdb("/tmp/King of Queens.ts", "King of Queens", overwrite_eit=True)
    if False:
        for file_name in dirList:
            file_name = path + file_name
            # only process supported file extensions and directories
            basename, ext = os.path.splitext(file_name)
            ext = ext.lower().replace('.', '')
            if not os.path.isdir(file_name):
                if not ext in supported:
                    if os.path.splitext(file_name)[1] == ".eit":
                        print "\nEIT info for: " + file_name
                        eit = EventInformationTable(file_name)
                        print "ID:0x%04X %s %s" % (eit.event_id, eit.start_time, eit.duration)
                        print eit.event_name
                        print eit.short_description
                        print eit.extended_description
                        print eit.getBeginTimeString()
                        print eit.duration / 60
                        print "Length: " + str(eit.descriptors_loop_length)
                        print "\n"
                    continue
    
            serviceref = eServiceReference(None, "4097:0:0:0:0:0:0:0:0:0:" + file_name)
            dvd = detectDVDStructure(serviceref.getPath())
            if dvd is not None:
                serviceref = eServiceReferenceDvd(serviceref, True)
            if ext == "iso":
                serviceref = eServiceReferenceDvd(serviceref)
            info = ServiceInfo(serviceref)
            eitFromTMDb(serviceref.getPath(), info.getName(), overwrite)
    
