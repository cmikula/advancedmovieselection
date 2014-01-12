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

import os, time, urllib
from struct import unpack, pack
from calendar import timegm
from MovieDB import tmdb, tvdb, downloadCover

def printStackTrace():
    import sys, traceback
    print "--- [AdvancedMovieSelection] STACK TRACE ---"
    traceback.print_exc(file=sys.stdout)
    print '-' * 50

def getLanguageCode(db):
    lng = db.getLocale()
    if lng == "ru":
        return "rus"
    return "DEU"

def toDate(mjd):
    year = int(((mjd - 15078.2) / 365.25))
    month = int(((mjd - 14956 - int(year * 365.25)) / 30.6001))
    day = int(mjd - 14956 - int(year * 365.25) - int(month * 30.6001))
    if month == 14 or month == 15:
        k = 1
    else:
        k = 0
    year += k;
    month += -1 - k * 12
    year += 1900
    return "%d.%02d.%02d" % (day, month, year)

def fromBCD(bcd):
    if ((bcd & 0xF0) >= 0xA0):
        return -1
    if ((bcd & 0xF) >= 0xA):
        return -1
    return ((bcd & 0xF0) >> 4) * 10 + (bcd & 0xF)

def parseDVBtime(t1, t2, t3, t4, t5, _hash=None):
    tm_sec = fromBCD(t5)
    tm_min = fromBCD(t4)
    tm_hour = fromBCD(t3)
    mjd = (t1 << 8) | t2

    tm_year = (int) ((mjd - 15078.2) / 365.25)
    tm_mon = (int) ((mjd - 14956.1 - (int)(tm_year * 365.25)) / 30.6001)
    tm_mday = (int) (mjd - 14956 - (int)(tm_year * 365.25) - (int)(tm_mon * 30.6001))
    if tm_mon == 14 or tm_mon == 15:
        k = 1
    else:
        k = 0
    tm_year = tm_year + k
    tm_mon = tm_mon - 1 - k * 12
    #tm_mon = tm_mon - 1
    tm_year += 1900

    #tm_isdst = 0
    #tm_gmtoff = 0

    if hash:
        _hash = tm_hour * 60 + tm_min
        _hash |= tm_mday << 11

    return timegm((tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec))

def toMJD(date):
    try:
        Y = int(date[0:4]) - 1900
        M = int(date[5:7])
        D = int(date[8:10])
        
        if M == 1 or M == 2:
            L = 1
        else: L = 0 
        MJD = 14956 + D + int ((Y - L) * 365.25) + int ((M + 1 + L * 12) * 30.6001)
        return MJD & 0xffff
    except:
        printStackTrace()
        return 51544
     
class Descriptor:
    def __init__(self):
        self.descriptor_length = 0

    def decode1(self, data):
        self.tag = ord(data[0])
        self.descriptor_length = ord(data[1])

    def encode1(self, data):
        data.append(pack('B', self.tag))
        data.append(pack('B', self.descriptor_length))
    
    @staticmethod
    def decode(data):
        print "Unsopported descriptor: 0x%X" % (unpack('B', data[0])[0])
        return ord(data[1]) + 2  

class TextDescriptor:
    def __init__(self, text):
        self.text = text
        self.length = len(self.text)
        
    def decode(self, data):
        self.length = ord(data[0])
        self.text = data[1:self.length + 1]

class ContentDescriptor(Descriptor):
    tag = 0x54
    def __init__(self, content, user):
        Descriptor.__init__(self)
        self.content_nibble_level_1 = (content >> 4) & 0x0f
        self.content_nibble_level_2 = content & 0x0f
        self.user = user
        self.descriptor_length = 2

    @staticmethod
    def decode(data, descriptor):
        descr = ContentDescriptor(ord(data[2]), ord(data[3]));
        print str(ord(data[0]))
        print str(ord(data[1]))
        print str(ord(data[2]))
        print str(ord(data[3]))
        descr.decode1(data)
        descr.content = ""
        content = descr.user
        if content == 0x00:
            descr.content = "Komödie"
        elif content == 0x01:
            descr.content = "Action"
        elif content == 0x02:
            descr.content = "Adventure"
        elif content == 0x03:
            descr.content = "Science fiction, Fantasy, Horror"
        elif content == 0x04:
            descr.content = "Comedy"
        elif content == 0x05:
            descr.content = "Soap"
        elif content == 0x06:
            descr.content = "Romance"
        elif content == 0x07:
            descr.content = "Drama"
        elif content == 0x08:
            descr.content = "Adult"
        print descr.content
        # TODO implement
        descriptor.append(descr)
        return descr.descriptor_length + 2  

class ItemDescriptor:
    def __init__(self, item_description, item):
        self.item_description = TextDescriptor(item_description)
        self.item = TextDescriptor(item)
        self.length = self.item_description.length + self.item.length

    def decode(self, data):
        self.item_description.decode(data)
        #data = data[descr.length+1:]
        #length = ord(data[0])
        #descr.item = data[1:length+1]

class ShortEventDescriptor(Descriptor):
    tag = 0x4D
    def __init__(self, event_name, text, language_code="DEU"):
        Descriptor.__init__(self)
        self.ISO_639_language_code = language_code
        self.event_name = TextDescriptor(event_name)
        self.text = TextDescriptor(text)
        self.descriptor_length = 5 + self.event_name.length + self.text.length  

    @staticmethod
    def decode(data, descriptor):
        descr = ShortEventDescriptor("", "")
        descr.decode1(data)
        descr.ISO_639_language_code = str(data[2:5])
        data = data[5:]
        descr.event_name.decode(data)
        data = data[descr.event_name.length + 1:]
        descr.text.decode(data) 
        #descr.descriptor_length = 7 + descr.event_name.length + descr.text.length
        descriptor.append(descr)
        #descriptor.append("\n\n")
        #descriptor.append(descr.text.text)
        return descr.descriptor_length + 2
    
    @staticmethod
    def encode(data, event_name, text, language_code="DEU"):
        if language_code == "rus":
            descr = ShortEventDescriptor(event_name.encode("iso8859_5", "ignore"), text.encode("iso8859_5", "ignore"), language_code)
        else:
            descr = ShortEventDescriptor(event_name.encode("cp1252", "ignore"), text.encode("cp1252", "ignore"), language_code)
        descr.encode1(data)
        data.append(descr.ISO_639_language_code)
        data.append(pack('B', descr.event_name.length))
        data.append(descr.event_name.text)
        data.append(pack('B', descr.text.length))
        data.append(descr.text.text)
 

class ExtendedEventDescriptor(Descriptor):
    tag = 0x4E
    def __init__(self, descriptor_number, last_descriptor_number, item_description, item, text, language_code="DEU"):
        Descriptor.__init__(self)
        #self.tag = ExtendedEventDescriptor.tag
        self.descriptor_number = descriptor_number & 0x0f
        self.last_descriptor_number = last_descriptor_number & 0x0f
        self.ISO_639_language_code = language_code
        self.length_of_items = 0
        self.item_description = ItemDescriptor(item_description, item)
        self.text = TextDescriptor(text)
        self.descriptor_length = 6 + self.item_description.length + self.text.length
        
    @staticmethod
    def decode(data, descriptor):
        descr = ExtendedEventDescriptor(0, 0, "", "", "")
        descr.decode1(data)
        descr.descriptor_number = ord(data[2]) >> 4
        descr.last_descriptor_number = ord(data[2]) & 0x0f
        descr.ISO_639_language_code = str(data[3:6])
        descr.length_of_items = ord(data[6])
        data = data[7:]
        descr.item_description.decode(data)
        if descr.length_of_items > 0:
            print "ExtendedEventDescriptor.length_of_items > 0 not implemented"
            data = data[descr.item_description.length + 1:]
            descr.text.decode(data) 
        #descr.descriptor_length = 7 + descr.event_name.length + descr.text.length
        descriptor.append(descr)
        return descr.descriptor_length + 2  

    @staticmethod
    def encode(data, item_description, language_code="DEU"):
        if language_code == "rus":
            text = item_description.encode("iso8859_5", "ignore")
        else:
            text = item_description.encode("cp1252", "ignore")
        descriptor_text = []
        length = len(text)
        while(length > 0):
            if len(text) > 248:
                descriptor_text.append(text[0:248])
                text = text[248:]
                length = len(text)
            else:
                descriptor_text.append(text)
                length = 0
        cnt = 0
        last_descriptor = len(descriptor_text) - 1
        for text in descriptor_text:
            descr = ExtendedEventDescriptor(cnt, last_descriptor, text, "", "", language_code)
            descr.encode1(data)
            data.append(pack('B', ((cnt << 4) & 0xf0) | (last_descriptor & 0x0f))) 
            data.append(descr.ISO_639_language_code)
            data.append(pack('B', descr.length_of_items))
            data.append(pack('B', descr.item_description.item_description.length))
            data.append(descr.item_description.item_description.text)
            cnt += 1

class ComponentDescriptor:
    tag = 0x50
    def __init__(self, text, language_code="DEU"):
        #self.tag = ComponentDescriptor.tag
        self.reserved_future_use = 0 >> 4
        self.stream_content = 0 & 0x0f
        self.component_type = 0
        self.component_tag = 0
        self.ISO_639_language_code = language_code
        self.text = text.encode("cp1252", "ignore")
        self.descriptor_length = 6 + len(self.text)
        
    @staticmethod
    def decode(data, descriptor):
        descr = ComponentDescriptor("")
        descr.tag = ord(data[0])
        descr.descriptor_length = ord(data[1])
        descr.reserved_future_use = ord(data[2]) >> 4
        descr.stream_content = ord(data[2]) & 0x0f
        descr.component_type = ord(data[3])
        descr.component_tag = ord(data[4])
        descr.ISO_639_language_code = str(data[5:8])
        descr.text = data[8:descr.descriptor_length + 2]
        descriptor.append(descr)
        return descr.descriptor_length + 2  

    @staticmethod
    def encode(data, text, language_code="DEU"):
        descr = ComponentDescriptor(text, language_code)
        data.append(pack('B', descr.tag))
        data.append(pack('B', descr.descriptor_length))
        data.append(pack('B', ((descr.reserved_future_use << 4) & 0xf0) | (descr.stream_content & 0x0f)))
        data.append(pack('B', descr.component_type))
        data.append(pack('B', descr.component_tag))
        data.append(descr.ISO_639_language_code)
        data.append(descr.text)

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

INV_CHARS = [(u"é", "e"), (u"Č", "C"), (u"č", "c"), (u"Ć", "c"), (u"ć", "c"), (u"Đ", "D"), (u"đ", "d"), (u"Š", "S"), (u"š", "s"),
             (u"Ž", "Z"), (u"ž", "z"), (u"„", "\""), (u"“", "\""), (u"”", "\""), (u"’", "'"), (u"‘", "'"), (u"«", "<"), (u"»", ">")]
 
def convertToUnicode(text):
    text = unicode(text)
    for ic in INV_CHARS:
        text = text.replace(ic[0], ic[1])
    return unicode(text)

def writeEIT(file_name, eit_file, name, overview, genre, extended_info, released, runtime, language_code="DEU"):
    _file = None
    try:
        data = []
        name = convertToUnicode(name)
        overview = convertToUnicode(overview)
        extended_info = convertToUnicode(extended_info)
        ShortEventDescriptor.encode(data, name, genre, language_code)
        ExtendedEventDescriptor.encode(data, overview + "\n" + extended_info, language_code)
        data = "".join(data)

        if runtime:
            rt = int(runtime)
            h = rt / 60
            m = rt - (60 * h)
            runtime = (h << 8) | (m / 10) << 4 | (m % 10)
        else:
            runtime = 0x0130
        
        event_id = 0x0000
        mjd = toMJD(released)
        start_time = 0x0000 #0x1915
        duration = runtime
        _id = len(data) & 0x0fff
        header = pack('>HHHBHBH', event_id, mjd, start_time, 0, duration, 0, _id)

        _file = open(eit_file, "wb")
        _file.write(header)
        _file.write(data)
        _file.close()
        return True
    except:
        if _file is not None:
            _file.close()
        printStackTrace()
        return False

def createEIT(file_name, title, movie=None, overwrite_eit=False, overwrite_cover=False, overwrite_backdrop=False):
    try:
        if title:
            title = title.replace("-", " ").replace("#", "%23")
        print "Fetching info for movie: " + str(title)
        # DVD directory
        if not os.path.isdir(file_name):
            f_name = os.path.splitext(file_name)[0]
        else:
            f_name = file_name
        eit_file = f_name + ".eit"
        jpg_file = f_name + ".jpg"
        backdrop_file = f_name + ".backdrop.jpg"
        
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

class EventInformationTable:
    def __init__(self, path, no_info=False):
        self.event_id = 0
        self.start_time = ""
        self.begin_time = 0
        self.date = ""
        self.duration = 0
        self.running_status = 0
        self.free_CA_mode = 0
        self.descriptors_loop_length = -1
        self.event_name = ""
        self.short_description = ""
        self.extended_description = ""
        self.components = []
        self.content_descriptor = []
        try:
            short_event_descriptor = []
            extended_event_descriptor = []
            component_descriptor = []
            content_descriptor = []
            #linkage_descriptor = []
            #parental_rating_descriptor = []
            if os.path.exists(path):
                print "EventInformationTable: " + path
                _file = open(path, "rb")
                data = _file.read(12)
                # Section event_id 16 bits
                self.event_id = unpack('>H', data[0:2])[0]
                # Section start_time 40 bits
                # 16 LSBs of MJD followed by 24 bits coded as 6 digits in 4-bit Binary Coded Decimal (BCD).
                self.begin_time = parseDVBtime(ord(data[2]), ord(data[3]), ord(data[4]), ord(data[5]), ord(data[6]))
                # Section duration 24 bits, skip seconds
                dur = unpack('BB', data[7:9])
                h = ((dur[0] >> 4) * 10) + (dur[0] & 0x0f) * 60
                m = ((dur[1] >> 4) * 10) + (dur[1] & 0x0f)
                self.duration = (h + m) * 60
                
                if no_info:
                    _file.close()
                    return
                # Section running_status 3 bits, free_CA_mode 1 bit, descriptors_loop_length 12 bits
                _id = unpack('>H', data[10:12])[0]
                self.running_status = _id >> 13
                self.free_CA_mode = (_id >> 12) & 0x01
                self.descriptors_loop_length = _id & 0xFFF
                
                data = _file.read()
                _file.close()
                pos = 0
                while pos < len(data):
                    rec = ord(data[0])
                    if rec == ShortEventDescriptor.tag:
                        length = ShortEventDescriptor.decode(data, short_event_descriptor)
                    elif rec == ExtendedEventDescriptor.tag:
                        length = ExtendedEventDescriptor.decode(data, extended_event_descriptor)
                    elif rec == ContentDescriptor.tag:
                        length = ContentDescriptor.decode(data, content_descriptor)
                    elif rec == ComponentDescriptor.tag:
                        length = ComponentDescriptor.decode(data, component_descriptor)
                    else:
                        length = Descriptor.decode(data)
                    data = data[length:]

                for descr in short_event_descriptor:
                    if descr.ISO_639_language_code.lower() == "rus":
                        self.event_name = descr.event_name.text.decode("iso8859_5").encode("utf-8")
                        self.short_description = descr.text.text.decode("iso8859_5").encode("utf-8")
                    else:
                        self.event_name = descr.event_name.text.decode("cp1252").encode("utf-8")
                        self.short_description = descr.text.text.decode("cp1252").encode("utf-8")
                text = []
                for descr in extended_event_descriptor:
                    #if descr.ISO_639_language_code.lower() == "deu":
                    text.append(descr.item_description.item_description.text)

                encoding = descr.ISO_639_language_code.lower() == "rus" and "iso8859_5" or "cp1252"
                self.extended_description = "".join(text).decode(encoding).encode("utf-8")
                for descr in component_descriptor:
                    if descr.ISO_639_language_code.lower() == "rus":
                        self.components.append(descr.text.decode("iso8859_5").encode("utf-8"))
                    else:
                        self.components.append(descr.text.decode("cp1252").encode("utf-8"))
                
        except:
            printStackTrace()
    
    def getEventName(self):
        return self.event_name
    
    def getShortDescription(self):
        return self.short_description

    def getExtendedDescription(self):
        return self.extended_description
    
    def getEventId(self):
        return self.event_id

    def getDuration(self):
        return self.duration

    def getBeginTimeString(self):
        return time.strftime("%d.%m.%Y %H:%M", time.gmtime(self.begin_time))
    
    def getBeginTime(self):
        return self.begin_time
    
    def getComponentData(self):
        return ""


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
    
