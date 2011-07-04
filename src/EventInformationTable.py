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

import os
from struct import unpack, pack
import tmdb, urllib
import time

def printStackTrace():
    import sys, traceback
    print '-' * 60
    traceback.print_exc(file=sys.stdout)
    print '-' * 60

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
    def __init__(self, tag):
        self.descriptor_tag = tag
        self.descriptor_length = 0

    def decode1(self, data):
        self.descriptor_tag = ord(data[0])
        self.descriptor_length = ord(data[1])

    def encode1(self, data):
        data.append(pack('B', self.descriptor_tag))
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
        Descriptor.__init__(self, ContentDescriptor.tag)
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
        Descriptor.__init__(self, ShortEventDescriptor.tag)
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
        descr = ShortEventDescriptor(event_name.encode("cp1252"), text.encode("cp1252"), language_code)
        descr.encode1(data)
        data.append(descr.ISO_639_language_code)
        data.append(pack('B', descr.event_name.length))
        data.append(descr.event_name.text)
        data.append(pack('B', descr.text.length))
        data.append(descr.text.text)
 

class ExtendedEventDescriptor(Descriptor):
    tag = 0x4E
    def __init__(self, descriptor_number, last_descriptor_number, item_description, item, text, language_code="DEU"):
        Descriptor.__init__(self, ExtendedEventDescriptor.tag)
        self.descriptor_tag = ExtendedEventDescriptor.tag
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
        text = item_description.encode("cp1252")
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
        self.descriptor_tag = ComponentDescriptor.tag
        self.reserved_future_use = 0 >> 4
        self.stream_content = 0 & 0x0f
        self.component_type = 0
        self.component_tag = 0
        self.ISO_639_language_code = language_code
        self.text = text.encode("cp1252")
        self.descriptor_length = 6 + len(self.text)
        
    @staticmethod
    def decode(data, descriptor):
        descr = ComponentDescriptor("")
        descr.descriptor_tag = ord(data[0])
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
        data.append(pack('B', descr.descriptor_tag))
        data.append(pack('B', descr.descriptor_length))
        data.append(pack('B', ((descr.reserved_future_use << 4) & 0xf0) | (descr.stream_content & 0x0f)))
        data.append(pack('B', descr.component_type))
        data.append(pack('B', descr.component_tag))
        data.append(descr.ISO_639_language_code)
        data.append(descr.text)
          

def createEIT(file_name, title, coverSize, overwrite_jpg=False, overwrite_eit=False, movie=None):
    file = None
    try:
        print "Fetching info for movie: " + title
        # DVD directory
        if not os.path.isdir(file_name):
            file_name = os.path.splitext(file_name)[0]
        else:
            file_name = file_name
        eit_file = file_name + ".eit"
        jpg_file = file_name + ".jpg"
        
        if (os.path.exists(jpg_file) and overwrite_jpg == False) and (os.path.exists(eit_file) and overwrite_eit == False):
            return True
        
        if movie == None:
            results = tmdb.search(title)
            if len(results) == 0:
                print "No info found for: " + title
                return False
            searchResult = results[0]
            movie = tmdb.getMovieInfo(searchResult['id'])
        
        if movie['name'] == None or movie['overview'] == None:
            print "No info found for: " + title
            return False

        print "Movie title: " + str(movie['name'])
        images = movie['images']
        cover_url = None
        if len(images) > 0:
            cover_url = movie['images'][0][coverSize]
        if not cover_url:
            print "No Cover found for", title, "\n"
        else:    
            if os.path.exists(jpg_file) and overwrite_jpg == False:
                print "File '%s' already exists, jpg download skipped!" % (jpg_file)
            else:
                urllib.urlretrieve (cover_url, jpg_file)

        if os.path.exists(eit_file) and overwrite_eit == False:
            print "File '%s' already exists, eit creation skipped!" % (eit_file)
            return True 
        
        original_name = movie['original_name']
        print "Original name:"
        print " " * 4, str(original_name)
        
        released = movie['released']
        print "Released:"
        print " " * 4, str(released)

        cast = movie['cast']
        if cast:
            has_director = False
            has_producer = False
            has_author = False
            has_actor = False
            for ca in cast:
                if ca == "director": has_director = True
                elif ca == "producer": has_producer = True
                elif ca == "author": has_author = True
                elif ca == "actor": has_actor = True
            if has_author:
                print "Authors:"
                for prodr in cast['author']:
                    print " " * 4, prodr['name']
            if has_director:
                print "Directors:"
                for prodr in cast['director']:
                    print " " * 4, prodr['name']
            if has_producer:
                print "Producers:"
                for prodr in cast['producer']:
                    print " " * 4, prodr['name']
            if has_actor:
                print "Actors:"
                for prodr in cast['actor']:
                    print " " * 4, prodr['name']
          
        genre = ""
        if len(movie['categories']):
            genre = " ".join(movie['categories']['genre'])
    
        runtime = movie['runtime']
        if runtime:
            rt = int(runtime)
            h = rt / 60
            m = rt - (60 * h)
            runtime = (h << 8) | (m / 10) << 4 | (m % 10)
        else:
            runtime = 0x0130
            
        name = movie['name']
        overview = movie['overview']
        if len(name) <= 2 or len(overview) <= 2:
            return False
        data = []
        ShortEventDescriptor.encode(data, name, genre)
        ExtendedEventDescriptor.encode(data, overview)
        data = "".join(data)
        
        event_id = 0x0000
        mjd = toMJD(released)
        start_time = 0x0000 #0x1915
        duration = runtime
        id = len(data) & 0x0fff
        header = pack('>HHHBHBH', event_id, mjd, start_time, 0, duration, 0, id)

        file = open(eit_file, "wb")
        file.write(header)
        file.write(data)
        file.close()
        return True
    except:
        if file is not None:
            file.close()
        printStackTrace()
        return False
        


class EventInformationTable:
    def __init__(self, path):
        self.event_id = 0
        self.start_time = ""
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
                file = open(path, "rb")
                data = file.read(12)
                # Section event_id 16 bits
                self.event_id = unpack('>H', data[0:2])[0]
                # Section start_time 40 bits
                # 16 LSBs of MJD followed by 24 bits coded as 6 digits in 4-bit Binary Coded Decimal (BCD).
                mjd = unpack('>H', data[2:4])[0]
                self.date = toDate(mjd)
                h = unpack('B', data[4:5])[0]
                ms = unpack('B', data[5:6])
#                h += int(time.daylight)
                h -= time.timezone / 3600
                if h & 0x08:
                    h += 0x10
                    h &= 0xF0
                if h >= 0x24:
                    h = h - 0x24
                self.start_time = "%x:%02x" % (h, ms[0])
                # Section duration 24 bits, skip seconds
                dur = unpack('BB', data[7:9])
                #h = int("%x" %(dur[0]))*60
                #m = int("%x" %(dur[1]))
                h = ((dur[0] >> 4) * 10) + (dur[0] & 0x0f) * 60
                m = ((dur[1] >> 4) * 10) + (dur[1] & 0x0f)
                self.duration = (h + m) * 60
                
                # Section running_status 3 bits, free_CA_mode 1 bit, descriptors_loop_length 12 bits
                id = unpack('>H', data[10:12])[0]
                self.running_status = id >> 13
                self.free_CA_mode = (id >> 12) & 0x01
                self.descriptors_loop_length = id & 0xFFF
                
                data = file.read()
                file.close()
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
                    #if descr.ISO_639_language_code.lower() == "deu":
                    self.event_name = descr.event_name.text.decode("cp1252").encode("utf-8")
                    self.short_description = descr.text.text.decode("cp1252").encode("utf-8")
                text = []
                for descr in extended_event_descriptor:
                    #if descr.ISO_639_language_code.lower() == "deu":
                    text.append(descr.item_description.item_description.text)
                self.extended_description = "".join(text).decode("cp1252").encode("utf-8")
                for descr in component_descriptor:
                    #if descr.ISO_639_language_code.lower() == "deu":
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
        return "%s, %s" % (self.date, self.start_time) 


def createEIT1(file_name, event_name, event_description, extended_description, components=[]):
    file = None
    try:
        print "Creating eit: " + file_name
        data = []
        ShortEventDescriptor.encode(data, event_name, event_description)
        ExtendedEventDescriptor.encode(data, extended_description)
        for descr in components:
            ComponentDescriptor.encode(data, descr)

        event_id = 0x27e5
        mjd = 0xd943
        start_time = 0x1915
        duration = 0x0155
        data = "".join(data)
        id = len(data) & 0x0fff
        header = pack('>HHHBHBH', event_id, mjd, start_time, 0, duration, 0, id)
        
        file = open(file_name + ".eit", "wb")
        file.write(header)
        file.write(data)
        file.close()
    except:
        if file is not None:
            file.close()
        printStackTrace()

def test():
    #movie_info = tmdb.getInfo(id[0])
    #imdb_data = tmdb.imdbResults(IMDB_TTID)
    #imdb_images = tmdb.imdbImages(IMDB_TTID)
    #tmdb_images = tmdb.tmdbImages(TMDB_MOVIE_ID)
    
    descr = ExtendedEventDescriptor("1", "2", "3")
    print str(descr.descriptor_length)
    descr = ShortEventDescriptor("1", "2")
    print str(descr.descriptor_length)
            

if __name__ == '__main__':
    #test()
    path = "./tmp/"
    dirList = os.listdir(path)
    for file_name in dirList:
        if os.path.splitext(file_name)[1] == ".meta":
            file = open(path + file_name)
            file.readline()
            title = file.readline()
            file.close()
            createEIT(path + "test1", title, "cover", overwrite_eit=True)
        if os.path.splitext(file_name)[1] == ".eit":
            print file_name
            eit = EventInformationTable(path + file_name)
            print "ID:0x%04X %s %s" % (eit.event_id, eit.start_time, eit.duration)
            print eit.event_name
            print eit.short_description
            print eit.extended_description
            print eit.getBeginTimeString()
            print eit.duration / 60
            print "Length: " + str(eit.descriptors_loop_length)
            print "\n"
            #createEIT1(path + "test", eit.event_name, eit.short_description, eit.extended_description, eit.components)

