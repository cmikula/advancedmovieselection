#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  Coded by cmikula & JackDaniel (c)2012
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

import os
from ServiceProvider import ServiceCenter, eServiceReferenceMarker
from ServiceDescriptor import MovieInfo
from enigma import iServiceInformation
from AccessRestriction import accessRestriction
from Globals import printStackTrace

class SortProvider():
    SORT_ALPHANUMERIC = 1
    SORT_RECORDED = 2
    SORT_DATE_ASC = 3
    SORT_DATE_DESC = 4
    SORT_DESCRIPTION = 5
    SORT_WITH_DIRECTORIES = 0x1000
    
    def sortMovieList(self, l, sort_type):
        sort_type = sort_type & (0xffff ^ SortProvider.SORT_WITH_DIRECTORIES)
        if sort_type == SortProvider.SORT_ALPHANUMERIC:
            l.sort(key=self.buildAlphaNumericSortKey)
        elif sort_type == SortProvider.SORT_DATE_ASC:
            l.sort(self.sortbyDateAsc)
        elif sort_type == SortProvider.SORT_DESCRIPTION:
            l.sort(self.sortbyDescription)
        else:
            l.sort(self.sortbyDateDesc)

    def sortbyDescription(self, a, b):
        d1 = a[0].info.getInfoString(a[0].serviceref, iServiceInformation.sDescription)
        d2 = b[0].info.getInfoString(b[0].serviceref, iServiceInformation.sDescription)
        return cmp(d1, d2)

    def sortbyDateAsc(self, a, b):
        return cmp(a[0].begin, a[0].begin)

    def sortbyDateDesc(self, a, b):
        return cmp(b[0].begin, a[0].begin)

    def sortFolders(self, a, b):
        return cmp(b[0].name.lower(), a[0].name.lower())

    def buildAlphaNumericSortKey(self, x):
        return (x[0].name and x[0].name.lower() or "", -x[0].begin)

    def sortEntries(self, a, b):
        return cmp(b.lower(), a.lower())


class MovieDatabase(dict, SortProvider):
    def __init__(self):
        dict.__init__(self)
        self.tags = []
        self['db'] = {}
    
    def clearAll(self):
        print "database clear all"
        self.tags = []
        self['db'].clear()

    def addTags(self, tags):
        tags |= set(self.tags)
        self.tags = sorted(tags)

    def getTags(self):
        return self.tags
    
    def getCreate(self, location):
        if not self["db"].has_key(location):
            #print "new locatio:", location
            item = {}
            item["movies"] = []
            item["dir_size"] = -1
            item["sort_type"] = -1
            self["db"][location] = item
            return item
        return self["db"][location]
    
    def addMovieList(self, location, movie_list, dir_size):
        print "database add:", location
        item = self.getCreate(location)
        item["movies"].extend(movie_list)
        item["dir_size"] = dir_size

    def setSortType(self, location, sort_type):
        item = self.getCreate(location)
        item["sort_type"] = sort_type

    def getSortType(self, location):
        if not self["db"].has_key(location):
            return -1
        return self["db"][location]["sort_type"]
        
    def addMovie(self, location, movie):
        self["db"][location]["movies"].append(movie)

    def removeLocation(self, location):
        print "database remove", location
        return self["db"].pop(location, None)

    def removeMovie(self, file_service_list):
        if not isinstance(file_service_list, list):
            file_service_list = [file_service_list]
        for service in file_service_list:
            file_name = isinstance(file_service_list, str) and service or service.getPath()
            print "try remove from list:", file_name
            for key, item in self["db"].iteritems():
                if not file_name.startswith(key):
                    continue
                for index, movie_info in enumerate(item["movies"]):
                    if movie_info.serviceref.getPath() == file_name:
                        del item["movies"][index]
                        print "success"

    def getMovieList(self, sort_type, filter_tags=None):
        l = []
        dirs = self.getDirectoryList(True)
        for location in dirs:
            item = self["db"][location]
            l1 = []
            for i in item["movies"]:
                this_tags = i.getTags()
                if not accessRestriction.isAccessible(this_tags):
                    continue
                if filter_tags is not None and not set(this_tags).issuperset(filter_tags):
                    continue
                l1.append((i,))
            
            if sort_type & SortProvider.SORT_WITH_DIRECTORIES and len(l1) > 2 and filter_tags is None:
                self.sortMovieList(l1, sort_type)
                name = location
                serviceref = eServiceReferenceMarker(location)
                serviceref.setName("[ " + name + " ]")
                info = ServiceCenter.getInstance().info(serviceref)
                mi = MovieInfo(name, serviceref, info)
                l1.insert(0, (mi,))
            l.extend(l1)
        if not sort_type & SortProvider.SORT_WITH_DIRECTORIES:
            self.sortMovieList(l, sort_type)
        return l
    
    def getDirectoryList(self, sort=False):
        if not sort:
            return self["db"].keys()
        return sorted(self["db"].keys())

    def getMissingLocations(self, dir_list):
        l = []
        for location in dir_list:
            root = os.path.realpath(location) + os.sep
            print "?", root
            if not self["db"].has_key(root):
                l.append(location) 
        print "missing locations", l
        return sorted(l)

    def getSubDirectories(self, location):
        l = []
        if not self["db"].has_key(location):
            return l
        for key, item in self["db"].iteritems():
            if key.startswith(location):
                l.append(key)
        return sorted(l)

    def findMovies(self, name):
        l = []
        for key, item in self["db"].iteritems():
            for index, movie_info in enumerate(item["movies"]):
                if movie_info.name == name:
                    l.append(movie_info)
        return l

    def findMoviePath(self, serviceref):
        if not serviceref:
            return
        movie_path = serviceref.getPath()
        for key, item in self["db"].iteritems():
            if not movie_path.startswith(key):
                continue
            for index, movie_info in enumerate(item["movies"]):
                if movie_info.serviceref.getPath() == movie_path:
                    return movie_info

    def getInfo(self, location):
        location = os.path.realpath(location) + os.sep
        if not self["db"].has_key(location):
            return
        movie_cnt = 0
        dir_cnt = -1
        size = 0
        dirs = self.getSubDirectories(location)
        for sub in dirs:
            item = self["db"][sub]
            movie_cnt += len(item["movies"])
            size += item["dir_size"]
            dir_cnt += 1
        if dir_cnt < 0:
            return None
        return (movie_cnt, dir_cnt, size)
    
    def getFullCount(self):
        directories = 0
        movies = 0
        for km in self["db"].iteritems():
            directories += 1
            movies += len(km[1]["movies"])
        return directories, movies

    def getSize(self, dir_path=None):
        cnt = 0
        size = 0
        if dir_path:
            dirs = self.getSubDirectories(dir_path)
            for sub in dirs:
                item = self["db"][sub]
                size += item["dir_size"]
                cnt += 1
            if cnt == 0:
                return -1
            return size
        for km in self["db"].iteritems():
            cnt += 1
            size += km[1]["dir_size"]
        if cnt == 0:
            return -1
        return size


from xml.dom.minidom import Document

class dict2xml(object):
    def __init__(self, structure):
        if len(structure) == 1:
            self.doc = Document()
            rootName = str(structure.keys()[0])
            self.root = self.doc.createElement(rootName)

            self.doc.appendChild(self.root)
            self.build(self.root, structure[rootName])

    def build(self, father, structure):
        if type(structure) == dict:
            for k in structure:
                if "/" in k:
                    tag = self.doc.createElement("location")
                    tag.setAttribute("path", k)
                    father.appendChild(tag)
                    self.build(tag, structure[k])
                else:
                    tag = self.doc.createElement(k)
                    father.appendChild(tag)
                    self.build(tag, structure[k])

        elif type(structure) == list:
            grandFather = father.parentNode
            tagName = father.tagName
            grandFather.removeChild(father)
            for l in structure:
                #tag = self.doc.createElement(tagName)
                self.build(father, l)
                grandFather.appendChild(father)

        elif isinstance(structure, MovieInfo):
            tag = self.doc.createElement("movie")
            tag.setAttribute("name", structure.name)
            tag.setAttribute("path", structure.path)
            tag.setAttribute("type", str(structure.type))
            tag.setAttribute("flags", str(structure.flags))
            father.appendChild(tag)
        else:
            data = str(structure)
            tag = self.doc.createTextNode(data)
            father.appendChild(tag)

    def display(self):
        print self.doc.toprettyxml(indent="  ")
    
    def write(self, file_name):
        try:
            xmlstr = self.doc.toprettyxml() #self.doc.toxml('utf-8')
            f = open(file_name, 'w')
            f.write(xmlstr)
            f.close()        
        except:
            printStackTrace()

if __name__ == '__main__':
    example = {'auftrag':{"kommiauftragsnr":2103839, "anliefertermin":"2009-11-25", "prioritaet": 7, "ort": u"Huecksenwagen", "positionen": [{"menge": 12, "artnr": "14640/XL", "posnr": 1}, ], "versandeinweisungen": [{"guid": "2103839-XalE", "bezeichner": "avisierung48h", "anweisung": "48h vor Anlieferung unter 0900-LOGISTIK avisieren"}, ]}}
    xml = dict2xml(example)
    xml.display()
