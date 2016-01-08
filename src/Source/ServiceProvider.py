#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#    Copyright (C) 2011 cmikula
#
#    In case of reuse of this source code please do not remove this copyright.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    For more information on the GNU General Public License see:
#    <http://www.gnu.org/licenses/>.
#
#    For example, if you distribute copies of such a program, whether gratis or for a fee, you 
#    must pass on to the recipients the same freedoms that you received. You must make sure 
#    that they, too, receive or can get the source code. And you must show them these terms so they know their rights.
#

import os
from Components.Element import cached
from Components.Sources.ServiceEvent import ServiceEvent as eServiceEvent
from enigma import eServiceCenter, iServiceInformation, eServiceReference
from Tools.Directories import fileExists
from EventInformationTable import EventInformationTable
from ServiceUtils import getFolderSize
from CueSheetSupport import CueSheet
from Globals import printStackTrace

instance = None

class ServiceTypes:
    idInvalid = eServiceReference.idInvalid     # -1
    idStructure = eServiceReference.idStructure # 0
    idDVB = eServiceReference.idDVB             # 1
    idFile = eServiceReference.idFile           # 2
    idUser = eServiceReference.idUser           # 4096
    idDVD = 0x1111 # 4369
    idMP3 = 0x1001 # 4097
    idBD = 0x0004

class ServiceFlags:
    isDirectory = eServiceReference.isDirectory # 1 # SHOULD enter  (implies mustDescent)
    mustDescent = eServiceReference.mustDescent # 2 # be played directly - often used with "isDirectory" (implies canDescent)
    canDescent = eServiceReference.canDescent   # 4 # supports enterDirectory/leaveDirectory
    flagDirectory = isDirectory | mustDescent | canDescent
    shouldSort = eServiceReference.shouldSort   # 8 # should be ASCII-sorted according to service_name. great for directories.
    hasSortKey = eServiceReference.hasSortKey   # 16 # has a sort key in data[3]. not having a sort key implies 0.
    sort1 = eServiceReference.sort1             # 32 # sort key is 1 instead of 0
    isMarker = eServiceReference.isMarker       # 64 # Marker
    isGroup = eServiceReference.isGroup         # 128 #is a group of services


def getServiceInfoValue(ref, what):
    # only works with ts files, if necessary use the ServiceCenter class
    info = eServiceCenter.getInstance().info(ref)
    v = ref and info.getInfo(ref, what) or info.getInfo(what)
    if v != iServiceInformation.resIsString:
        return ""
    return ref and info.getInfoString(ref, what) or info.getInfoString(what)


class eServiceReferenceVDir(eServiceReference):
    def __init__(self, file_name):
        eServiceReference.__init__(self, eServiceReference.idFile, ServiceFlags.flagDirectory | ServiceFlags.isMarker, file_name)

class eServiceReferenceMarker(eServiceReference):
    def __init__(self, file_name):
        eServiceReference.__init__(self, eServiceReference.idUser, ServiceFlags.flagDirectory | ServiceFlags.isMarker, file_name)

class eServiceReferenceBackDir(eServiceReference):
    def __init__(self, file_name):
        eServiceReference.__init__(self, eServiceReference.idUser, eServiceReference.flagDirectory, file_name)

class eServiceReferenceListAll(eServiceReference):
    def __init__(self, file_name):
        eServiceReference.__init__(self, eServiceReference.idUser, eServiceReference.flagDirectory, file_name)

class eServiceReferenceHotplug(eServiceReference):
    def __init__(self, file_name):
        eServiceReference.__init__(self, eServiceReference.idUser, eServiceReference.flagDirectory, file_name)


class eServiceReferenceBludisc(eServiceReference):
    def __init__(self, serviceref, isStruct=False):
        idx = 0
        eServiceReference.__init__(self, ServiceTypes.idDVD, 0, serviceref.getPath())
        #eServiceReference.__init__(self, 0x04, 0, "%s:%03d" % (serviceref.getPath(), idx))
        self.isStruct = isStruct
        if isStruct is True:
            # remove trailing slash
            self.setPath(serviceref.getPath()[0:-1])
            self.setName(os.path.basename(self.getPath()))
            self.flags = eServiceReference.isDirectory
        else:
            self.setName(os.path.basename(os.path.splitext(serviceref.getPath())[0]))
        self.bludisc_path = self.getPath()

    def getBludisc(self):
        if self.isStruct is True:
            return self.bludisc_path + "/"
        else:
            return self.bludisc_path

    def setBludisc(self, path):
        self.bludisc_path = path


class eServiceReferenceDvd(eServiceReference):
    def __init__(self, serviceref, dvdStruct=False):
        eServiceReference.__init__(self, ServiceTypes.idDVD, 0, serviceref.getPath())
        self.dvdStruct = dvdStruct
        if dvdStruct is True:
            # remove trailing slash
            self.setPath(self.getPath()[0:-1])
            self.setName(os.path.basename(self.getPath()))
            self.flags = eServiceReference.isDirectory
        else:
            self.setName(os.path.basename(os.path.splitext(self.getPath())[0]))
            
    def getDVD(self):
        if self.dvdStruct is True:
            return [self.getPath() + "/"]
        else:
            return [self.getPath()]
        
    def isIsoImage(self):
        return not self.dvdStruct


def detectBludiscStructure(loadPath):
    if not os.path.isdir(loadPath):
        return None
    if fileExists(loadPath + "BDMV/"):
        return loadPath + "BDMV/"
    return None


def detectDVDStructure(loadPath):
    if not os.path.isdir(loadPath):
        return None
    if fileExists(loadPath + "VIDEO_TS.IFO"):
        return loadPath + "VIDEO_TS.IFO"
    if fileExists(loadPath + "VIDEO_TS/VIDEO_TS.IFO"):
        return loadPath + "VIDEO_TS/VIDEO_TS.IFO"
    return None


import struct
from Screens.InfoBarGenerics import InfoBarCueSheetSupport
def getPercentSeen(serviceref):
    cuts = serviceref.getPath() + ".cuts"
    if serviceref.type == eServiceReference.idDVB:
        meta = serviceref.getPath() + ".meta"
    else:
        meta = serviceref.getPath() + ".ts.meta"
    
    length = 0
    last = 0
    perc = 0
    f = None
    if not os.path.exists(cuts) or not os.path.exists(meta):
        return 0
    try:
        f = open(cuts, "rb")
        while 1:
            data = f.read(12)
            if data == '':
                break
            what = struct.unpack('>I', data[8:12])[0]
            if what == InfoBarCueSheetSupport.CUT_TYPE_LAST:
                where = struct.unpack('>Q', data[0:8])[0]
                last = long(where) / 90000
            if what == InfoBarCueSheetSupport.CUT_TYPE_OUT:
                where = struct.unpack('>Q', data[0:8])[0]
                length = long(where) / 90000
        f.close()
        
        if last > 0 and length == 0:
            f = open(meta, "rb")
            lines = f.readlines()
            if len(lines) > 5:
                length = long(lines[5]) / 90000
        
        if last > 0 and length > 0:
            perc = int((float(last) / length) * 100)
            if perc > 100:
                perc = 100
            if perc < 0:
                perc = 0
        print meta
        print length
        print perc
    except:
        printStackTrace()
    finally:
        if f is not None:
            f.close()
    return perc


class ServiceCenter:
    def __init__(self):
        global instance
        instance = eServiceCenter.getInstance()
        instance.info = self.info
        
    @staticmethod
    def getInstance():
        if instance is None:
            ServiceCenter()
        return instance
        
    def info(self, serviceref):
        info = eServiceCenter.getInstance().info(serviceref)
        if info is not None:
            if serviceref.getPath().endswith(".ts"):
                info.cueSheet = CueSheet(serviceref) 
                return info
            return Info(serviceref)
        else:
            return Info(serviceref)


class ServiceEvent(eServiceEvent):
    def __init__(self):
        eServiceEvent.__init__(self)

    @cached
    def getInfo(self):
        return self.service and ServiceCenter.getInstance().info(self.service)

    info = property(getInfo)


def checkCreateMetaFile(serviceref):
    if not serviceref.flags & eServiceReference.mustDescent:
        if serviceref.type == eServiceReference.idDVB:
            meta_path = serviceref.getPath() + ".meta"
        else:
            meta_path = serviceref.getPath() + ".ts.meta"
        if not os.path.exists(meta_path):
            if serviceref.getPath()[-3:] in ("mp3", "ogg", "wav", "m4a"):
                return None
            if os.path.isfile(serviceref.getPath()):
                title = os.path.basename(os.path.splitext(serviceref.getPath())[0])
            else:
                title = serviceref.getName()
            lt = long(os.stat(serviceref.getPath()).st_mtime)
            print "create new metafile"
            print serviceref.toString()
            print lt
            sid = "%d:%d:0:0:0:0:0:0:0:0:"%(serviceref.type, serviceref.flags)
            descr = ""
            time = lt
            tags = ""
            metafile = open(meta_path, "w")
            metafile.write("%s\n%s\n%s\n%d\n%s\n" % (sid, title, descr, time, tags))
            metafile.close()
        
        return meta_path


class ServiceInfo:
    def __init__(self, serviceref):
        self.servicename = ""
        self.description = ""
        self.tags = ""
        self.name = ""
        self.time_create = ""
        try:
            try:
                meta_path = checkCreateMetaFile(serviceref)
            except Exception, e:
                print e
            if meta_path is None:
                if os.path.isfile(serviceref.getPath()):
                    self.name = os.path.splitext(os.path.basename(serviceref.getPath()))[0]
                else:
                    self.name = serviceref.getName()
                return
            
            if meta_path is not None and os.path.exists(meta_path):
                meta_file = open(meta_path, "r")
                meta_file.readline()
                self.name = meta_file.readline().rstrip("\r\n")
                self.description = meta_file.readline().rstrip("\r\n")
                self.time_create = meta_file.readline().rstrip("\r\n")
                self.tags = meta_file.readline().rstrip("\r\n")
                meta_file.close()
        except Exception, e:
            print "Exception in load meta data: " + str(e)
            printStackTrace()

    def getServiceName(self):
        return self.servicename

    def getName(self):
        return self.name

    def getDescription(self):
        return self.description

    def getTags(self):
        return self.tags


class Info:
    def __init__(self, serviceref):
        self.cue = CueSheet(serviceref)
        self.serviceInfo = ServiceInfo(serviceref)
        self.length = 0
        self.end = 0
        self.last = 0
        serviceref.cueSheet = self.cueSheet

    def cueSheet(self):
        return self.cue
    
    def getLength(self, serviceref):
        cut_list = self.cue.getCutList()
        for (pts, what) in cut_list:
            if what == InfoBarCueSheetSupport.CUT_TYPE_OUT:
                self.length = pts / 90000
        if self.length == 0:
            file_name = serviceref.getPath()
            if not os.path.isdir(file_name):
                eit_file = os.path.splitext(file_name)[0] + ".eit"
            else:
                eit_file = file_name + ".eit"
            self.length = EventInformationTable(eit_file, True).getDuration()
        return self.length
    
    def getInfoString(self, serviceref, type):
        if type == iServiceInformation.sServiceref:
            return "iServiceInformation.sServiceref"
        if type == iServiceInformation.sDescription:
            return self.serviceInfo.description
        if type == iServiceInformation.sTags:
            return self.serviceInfo.tags
        return "None"

    def getInfo(self, serviceref, type):
        if type == iServiceInformation.sTimeCreate:
            if os.path.exists(serviceref.getPath()):
                if self.serviceInfo.time_create:
                    return long(self.serviceInfo.time_create)
                return long(os.stat(serviceref.getPath()).st_mtime) 
        return None
    
    def getInfoObject(self, serviceref, type):
        if type == iServiceInformation.sFileSize:
            try:
                dvd = detectDVDStructure(serviceref.getPath() + "/")
                if dvd:
                    return getFolderSize(os.path.dirname(dvd))
                return os.path.getsize(serviceref.getPath())
            except Exception, e:
                print e
                return -1
        return None
    
    def getServiceReference(self):
        return self.serviceInfo
    
    def getName(self, serviceref):
        if self.serviceInfo.name:
            return self.serviceInfo.name
        else:
            return serviceref.getName()
    
    def getEvent(self, serviceref):
        file_name = serviceref.getPath()
        if serviceref.flags & eServiceReference.mustDescent:
            eit_file = file_name + ".eit"
            if os.path.exists(eit_file):
                return EventInformationTable(eit_file)
            from ServiceDescriptor import DirectoryEvent
            return DirectoryEvent(serviceref)
        if not serviceref.flags & eServiceReference.isDirectory:
            eit_file = os.path.splitext(file_name)[0] + ".eit"
        else:
            eit_file = file_name + ".eit"

        if os.path.exists(eit_file):
            return EventInformationTable(eit_file)
        return Event(self, serviceref)


class Event:
    def __init__(self, info, serviceref):
        self.info = info
        self.serviceref = serviceref
    
    def getEventName(self):
        return self.info.serviceInfo.name
    
    def getShortDescription(self):
        return self.info.serviceInfo.description

    def getExtendedDescription(self):
        return ""

    def getEventId(self):
        return 0

    def getBeginTimeString(self):
        from datetime import datetime
        begin = self.info.getInfo(self.serviceref, iServiceInformation.sTimeCreate)
        d = datetime.fromtimestamp(begin)
        return d.strftime("%d.%m.%Y %H:%M")
    
    def getDuration(self):
        return self.info.length
    
    def getBeginTime(self):
        return self.info.getInfo(self.serviceref, iServiceInformation.sTimeCreate)
    
    def getComponentData(self):
        return ""

