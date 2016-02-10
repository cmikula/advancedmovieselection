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
        cert = tmdb.decodeCertification(movie.releases)
        if cert:
            from AccessRestriction import accessRestriction
            accessRestriction.setToService(file_name, cert)
    except Exception, e:
        print e


def createEIT(file_name, title, movie=None, overwrite_eit=False, overwrite_cover=False, overwrite_backdrop=False):
    try:
        if title:
            title = title.replace("-", " ").replace("#", "%23")
        # DVD directory
        if not os.path.isdir(file_name):
            f_name = os.path.splitext(file_name)[0]
        else:
            f_name = file_name
        eit_file = f_name + ".eit"
        jpg_file = f_name + ".jpg"
        backdrop_file = f_name + ".backdrop.jpg"
        
        # check and cancel if all exists
        if (not overwrite_eit and os.path.exists(eit_file)) and \
        (not overwrite_cover and os.path.exists(jpg_file)) and \
        (not overwrite_backdrop and os.path.exists(backdrop_file)):
            print "Cancel all data exists:", str(title)
            return

        print "Fetching info for movie: " + str(title)
        
        if movie == None:
            tmdb3 = tmdb.init_tmdb3()
            results = tmdb3.searchMovie(title)
            if len(results) == 0:
                print "No info found for: " + str(title)
                return False
            searchResult = None
            # locate fully agreement in list
            for result in results:
                if result.title == title:
                    searchResult = result
                    break
            # if not identify one result select first item
            if not searchResult:
                searchResult = results[0]
            movie = searchResult

        name = movie.title
        overview = movie.overview
        runtime = movie.runtime
        genre = []
        for x in movie.genres:
            genre.append(x.name)
        genre = " ".join(genre)

        # update certificate and meta genre
        appendShortDescriptionToMeta(file_name, genre)
        setTmdbCertificationtion(movie, file_name)
        
        if name:
            print "Movie title: " + name.encode("utf-8", "ignore")

        downloadCover(movie.poster_url, jpg_file, overwrite_cover)
        downloadCover(movie.backdrop_url, backdrop_file, overwrite_backdrop)

        if os.path.exists(eit_file) and overwrite_eit == False:
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

        directors = [x.name for x in movie.crew if x.job == 'Director']
        actors = [x.name for x in movie.cast]
        # print out extended movie informations
        try:
            #original_name = movie['original_name']
            #print "Original name:"
            #print " " * 4, str(original_name)
            
            released = movie.releasedate
            print "Released:"
            print " " * 4, str(released)
    
            for cast in movie.cast:
                print cast.name
        except Exception, e:
            print e

        ex_info = []
        if released:
            try:
                try:
                    print movie.countries
                    # countries = [c.name for c in movie.countries]
                    countries = [c.code for c in movie.countries]
                    country = ", ".join(countries) + " "
                    country = country.replace("US", "USA").replace("DE", "GER")
                except:
                    country = ""
                year = str(released.year)
                ex_info.append(country + year) 
            except Exception, e:
                print e
        else:
            try:
                countries = [c.code for c in movie.countries]
                country = ", ".join(countries) + " "
                country = country.replace("US", "USA").replace("DE", "GER")
                ex_info.append(country) 
            except:
                pass

        if runtime:
            try:
                rt = str(int(runtime))
                ex_info.append(rt + " Min") 
            except Exception, e:
                print e
        
        if len(directors) > 0:
            ex_info.append("Von " + ", ".join(directors))
        if len(actors) > 0:
            ex_info.append("Mit " + ", ".join(actors))
        extended_info = ". ".join(ex_info)
        print "Overview:"
        print " " * 4, overview
        print "Extended info:"
        print " " * 4, extended_info
        
        language_code = getLanguageCode(tmdb)
        return writeEIT(file_name, eit_file, name, overview, genre, extended_info, str(released), runtime, language_code)
    except:
        printStackTrace()
        return False
        
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
    file_name = "./tmp/eit_test.mkv"
    eit_file = "./tmp/eit_test.eit"
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
    path = "./tmp/"
    if not os.path.exists(path):
        os.makedirs(path) 

    testMultiEit()
    tmdb.setLocale('de')
    createEIT("./tmp/Fight Club.ts", "Fight Club", "cover", overwrite_eit=True)
    tmdb.setLocale('ru')
    createEIT("./tmp/Blitz_ru.ts", "Черная Молния", "cover", overwrite_eit=True)
    tmdb.setLocale('de')
    printEIT("./tmp/Blitz_ru.eit")
    printEIT("./tmp/russia.eit")
    printEIT("./tmp/Shutter Island ru Original.eit")
    printEIT("./tmp/Shutter Island ru tmdb.eit")

    printEIT("./tmp/22 Bullets.eit")

    results = tvdb.search("Law & Order")
    #results = search("The Mentalist")
    for searchResult in results:
        movie = tvdb.getMovieInfo(searchResult['id'])
        serie = movie['Serie'][0]
        episode = tvdb.searchEpisode(movie['Episode'], "Die Wunderdoktorin")
        if episode:
            createEITtvdb("./tmp/Law & Order.ts", None, overwrite_eit=True, serie=serie, episode=episode)

    supported = ["ts", "iso", "mkv"]
    dirList = os.listdir(path)
    printEIT("./tmp/22 Bullets.eit")
    createEIT("./tmp/22 Bullets.ts", "22 Bullets", "cover", overwrite_eit=True)
    createEITtvdb("./tmp/King of Queens.ts", "King of Queens", overwrite_eit=True)
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
            createEIT(serviceref.getPath(), info.getName(), "cover", overwrite_eit=False)
    
