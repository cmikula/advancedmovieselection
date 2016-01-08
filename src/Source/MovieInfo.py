#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  Coded by cmikula (c)2015
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

from enigma import eServiceReference, iServiceInformation

class MovieInfo():
    idDVB = eServiceReference.idDVB
    idDVD = 0x1111 # 4369
    idMP3 = 0x1001 # 4097
    idBD = 0x0004
    def __init__(self, name, serviceref, info=None, begin=-1, length=-1, file_name=None, size=0):
        self.name = name
        self.info = info
        self.begin = begin
        self.length = length
        self.size = size
        self.serviceref = serviceref
        self.percent = -1
        if serviceref:
            self.flags = serviceref.flags
            self.type = serviceref.type
            self.path = serviceref.getPath()
            self.s_type = type(serviceref)
        else:
            self.flags = 0
            self.type = self.idDVB
            self.path = file_name
            self.s_type = eServiceReference

    def createService(self):
        #print "x" * 80
        #print self.path
        if self.s_type == eServiceReference:
            serviceref = self.s_type(self.type, self.flags, self.path)
        else:
            serviceref = self.s_type(self.path)
        if self.flags & eServiceReference.mustDescent:
            serviceref.setName(self.name)
        return serviceref

    #serviceref = property(createService)

    def getPath(self):
        return self.path
    
    def getTags(self):
        if self.info is None:
            return []
        this_tags = self.info.getInfoString(self.serviceref, iServiceInformation.sTags).split(' ')
        if this_tags is None or this_tags == ['']:
            this_tags = []
        return this_tags
