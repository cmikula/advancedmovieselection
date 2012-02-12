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

from Components.Element import cached
from Components.Sources.ServiceEvent import ServiceEvent as eServiceEvent
from enigma import eServiceCenter, iServiceInformation, eServiceReference
from Tools.Directories import fileExists
from EventInformationTable import EventInformationTable
from Components.config import config
from Screens.InfoBarGenerics import InfoBarCueSheetSupport
import struct
import os
from shutil import copyfile

if fileExists("/usr/lib/enigma2/python/Plugins/Bp/geminimain/plugin.pyo"):
    __CONF__ = "/etc/enigma2/gemini_DateiBrowser.conf"
else:
    __CONF__ = "/etc/enigma2/AdvancedMovieSelection.conf"

if not fileExists(__CONF__):
    copyfile("/usr/lib/enigma2/python/Plugins/Extensions/AdvancedMovieSelection/AdvancedMovieSelection.conf", __CONF__)
DMCONFFILE = __CONF__

instance = None

def getServiceInfoValue(ref, what):
    info = eServiceCenter.getInstance().info(ref)
    v = ref and info.getInfo(ref, what) or info.getInfo(what)
    if v != iServiceInformation.resIsString:
        return ""
    return ref and info.getInfoString(ref, what) or info.getInfoString(what)

class PicLoader:
    def __init__(self, width, height):
        from enigma import ePicLoad
        from Components.AVSwitch import AVSwitch
        self.picload = ePicLoad()
        sc = AVSwitch().getFramebufferScale()
        self.picload.setPara((width, height, sc[0], sc[1], False, 1, "#00000000"))

    def load(self, filename):
        self.picload.startDecode(filename, 0, 0, False)
        return self.picload.getData()

class eServiceReferenceDvd(eServiceReference):
    def __init__(self, serviceref, dvdStruct=False):
        eServiceReference.__init__(self, "4097:0:0:0:0:0:0:0:0:0:" + serviceref.getPath())
        self.dvdStruct = dvdStruct
        if dvdStruct is True:
            # remove trailing slash
            self.setPath(self.getPath()[0:-1])
            self.setName(os.path.basename(self.getPath()))
        else:
            self.setName(os.path.basename(os.path.splitext(self.getPath())[0]))
            
    def getDVD(self):
        if self.dvdStruct is True:
            return [self.getPath() + "/"]
        else:
            return [self.getPath()]

class MovieConfig:
    def __init__(self):
        self.readDMconf()
        
    def readDMconf(self):
        self.hidelist = []
        self.hotplug = []
        self.rename = []
        try:
            rfile = open(DMCONFFILE, 'r')
            for x in rfile.readlines():
                val = x.strip()
                if val.startswith('#'):
                    self.hotplug.append(val[1:])
                elif val.startswith('%'):
                    self.rename.append(val[1:])
                else:
                    self.hidelist.append(val)
            rfile.close()
        except:
            pass

    def isHidden(self, name):
        return name in self.hidelist

    def isHiddenHotplug(self, name):
        return name in self.hotplug

    def getRenamedName(self, name):
        try:
            for item in self.rename:
                i = item.split("\t")
                if i[0] == name:
                    return i[1] 
        except:
            pass
        return name
    
    def safe(self):
        try:
            f = open(DMCONFFILE, 'w')
            for x in self.hidelist:
                f.write(x + "\r\n")
            for x in self.hotplug:
                f.write('#' + x + "\r\n")
            for x in self.rename:
                f.write('%' + x + "\r\n")
            f.close()
        except Exception, e:
            print e

def getFolderSize(loadPath):
    folder_size = 0
    for (path, dirs, files) in os.walk(loadPath):
        for file in files:    
            filename = os.path.join(path, file)    
            if os.path.exists(filename):
                folder_size += os.path.getsize(filename)
    return folder_size

def getDirSize(root):
    folder_size = 0
    for filename in os.listdir(root):
        p = os.path.join(root, filename)
        if os.path.exists(p):
            folder_size += os.path.getsize(p)
    return folder_size

def detectDVDStructure(loadPath):
    if not os.path.isdir(loadPath):
        return None
    if fileExists(loadPath + "VIDEO_TS.IFO"):
        return loadPath + "VIDEO_TS.IFO"
    if fileExists(loadPath + "VIDEO_TS/VIDEO_TS.IFO"):
        return loadPath + "VIDEO_TS/VIDEO_TS.IFO"
    return None

class ServiceCenter:
    def __init__(self):
        global instance
        instance = eServiceCenter.getInstance()
        instance.info = self.info
        
    @staticmethod
    def getInstance():
        global instance
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

def hasLastPosition(service):
    fileName = service.getPath()
    file = None
    if not os.path.exists(fileName + ".cuts"):
        return False
    try:
        file = open(fileName + ".cuts", "rb")
        while 1:
            data = file.read(12)
            if data == '':
                break
            what = struct.unpack('>I', data[8:12])[0]
            if what == InfoBarCueSheetSupport.CUT_TYPE_LAST:
                return True
    except:
        pass
    finally:
        if file is not None:
            file.close()
    return False

def writeCutList(fileName, cutList):
    file = None
    try:
        file = open(fileName + ".cuts", "wb")
        for where, what in cutList:
            data = struct.pack('>Q', where)
            file.write(data)
            data = struct.pack('>I', what)
            file.write(data)
    except Exception, e:
        print "Exception in writeCutList: " + str(e)
    finally:
        if file is not None:
            file.close()

def getCutList(fileName):
    file = None
    cutList = [ ]
    if not os.path.exists(fileName + ".cuts"):
        return cutList
    try:
        file = open(fileName + ".cuts", "rb")
        while 1:
            data = file.read(12)
            if data == '':
                break
            where = struct.unpack('>Q', data[0:8])[0]
            what = struct.unpack('>I', data[8:12])[0]
            cutList.append((where, what))
    except Exception, e:
        print "Exception in getCutList: " + str(e)
    finally:
        if file is not None:
            file.close()
    return cutList

def checkDVDCuts(fileName):
    file = None
    cutList = [ ]
    if not os.path.exists(fileName + ".cuts"):
        return False
    try:
        file = open(fileName + ".cuts", "rb")
        #resume_info.title=%d, chapter=%d, block=%lu, audio_id=%d, audio_lock=%d, spu_id=%d, spu_lock=%d
        while 1:
            data = file.read(12)
            if data == '':
                break
            where = struct.unpack('>Q', data[0:8])[0]
            what = struct.unpack('>I', data[8:12])[0]
            print what, where
            cutList.append((where, what))
            
            title = struct.unpack('<i', file.read(4))[0:4][0]
            chapter = struct.unpack('<i', file.read(4))[0:4][0]
            block = struct.unpack('<I', file.read(4))[0:4][0]
            audio_id = struct.unpack('<i', file.read(4))[0:4][0]
            audio_lock = struct.unpack('<i', file.read(4))[0:4][0]
            spu_id = struct.unpack('<i', file.read(4))[0:4][0]
            spu_lock = struct.unpack('<i', file.read(4))[0:4][0]
            what = struct.unpack('>i', file.read(4))[0:4][0]
            print "py_resume_pos: resume_info.title=%d, chapter=%d, block=%d, audio_id=%d, audio_lock=%d, spu_id=%d, spu_lock=%d  (pts=%d)" % (title, chapter, block, audio_id, audio_lock, spu_id, spu_lock, what)
            if what == 4:
                return True 
    except Exception, e:
        print "Exception in checkDVDCutList: " + str(e)
    finally:
        if file is not None:
            file.close()
    return False

def checkCreateMetaFile(ref):
    file = ref.getPath() + ".ts.meta"
    if not os.path.exists(file):
        if os.path.isfile(ref.getPath()):
            title = os.path.basename(os.path.splitext(ref.getPath())[0])
        else:
            title = ref.getName()
        sid = ""
        descr = ""
        time = ""
        tags = ""
        metafile = open(file, "w")
        metafile.write("%s\r\n%s\r\n%s\r\n%s\r\n%s" % (sid, title, descr, time, tags))
        metafile.close()

class ServiceInfo:
    def __init__(self, serviceref):
        self.servicename = ""
        self.description = ""
        self.tags = ""
        try:
            try:
                meta_path = serviceref.getPath() + ".ts.meta"
                checkCreateMetaFile(serviceref)
            except Exception, e:
                print e
                if os.path.isfile(serviceref.getPath()):
                    self.name = os.path.basename(serviceref.getPath()).split('.')[0]
                else:
                    self.name = serviceref.getName()
                return
            if os.path.exists(meta_path):
                file = open(meta_path, "r")
                file.readline()
                self.name = file.readline().rstrip("\r\n")
                self.description = file.readline().rstrip("\r\n")
                file.readline()
                self.tags = file.readline().rstrip("\r\n")
                file.close()
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

class CueSheet:
    def __init__(self, serviceref):
        self.serviceref = serviceref
    
    def __call__(self):
        return self
    
    def getCutList(self):
        return getCutList(self.serviceref.getPath())

    def setCutList(self, cut_list):
        writeCutList(self.serviceref.getPath(), cut_list)

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
            if what == 1:
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
                return long(os.stat(serviceref.getPath()).st_mtime)
        return None
    
    def getInfoObject(self, serviceref, type):
        if type == iServiceInformation.sFileSize:
            dvd = detectDVDStructure(serviceref.getPath() + "/")
            if dvd:
                return getFolderSize(os.path.dirname(dvd))
            return os.path.getsize(serviceref.getPath())
        return None
    
    def getServiceReference(self):
        return self.serviceInfo
    
    def getName(self, serviceref):
        return self.serviceInfo.name
    
    def getEvent(self, serviceref):
        file_name = serviceref.getPath()
        if not os.path.isdir(file_name):
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
        pass
    
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

from Components.Converter.Converter import Converter
class EventName(Converter, object):
    NAME = 0
    SHORT_DESCRIPTION = 1
    EXTENDED_DESCRIPTION = 2
    ID = 3
    
    def __init__(self, type):
        Converter.__init__(self, type)
        if type == "Description":
            self.type = self.SHORT_DESCRIPTION
        elif type == "ExtendedDescription":
            self.type = self.EXTENDED_DESCRIPTION
        elif type == "ID":
            self.type = self.ID
        else:
            self.type = self.NAME

    @cached
    def getText(self):
        event = self.source.event
        if event is None:
            return ""
            
        if self.type == self.NAME:
            return event.getEventName()
        elif self.type == self.SHORT_DESCRIPTION:
            return event.getShortDescription()
        elif self.type == self.EXTENDED_DESCRIPTION:
            return event.getExtendedDescription()
        elif self.type == self.ID:
            return str(event.getEventId())
        
    text = property(getText)


class CutListSupport:
    def __init__(self, service):
        self.currentService = service
        self.cut_list = [ ]

    def getCuesheet(self):
        service = self.session.nav.getCurrentService()
        if service is None:
            return None
        return service.cueSheet()

    def downloadCuesheet(self):
        try:
            cue = self.getCuesheet()
            if cue is None or isinstance(self.currentService, eServiceReferenceDvd):
                print "download failed, no cuesheet interface! Try to load from cuts"
                self.cut_list = [ ]
                if self.currentService is not None:
                    cutList = getCutList(self.currentService.getPath())
                    if cutList is not None:
                        self.cut_list = cutList
                # FIXME dvd player not start
                #if len(self.cut_list) == 0 and isinstance(self.currentService, eServiceReferenceDvd):
                #    self.cut_list = [(0, 3)]
            else:
                self.cut_list = cue.getCutList()
            if config.usage.on_movie_start.value == "beginning" or config.usage.on_movie_start.value == "ask" and config.AdvancedMovieSelection.jump_first_mark.value == True:
                self.jumpToFirstMark()
            stop_before_end_time = int(config.AdvancedMovieSelection.stop_before_end_time.value) 
            if stop_before_end_time > 0:
                pos = self.getCuePositions()
                if ((pos[0] - pos[1]) / 60) < stop_before_end_time:
                    self.ENABLE_RESUME_SUPPORT = False
                else:
                    self.ENABLE_RESUME_SUPPORT = True

        except Exception, e:
            print "DownloadCutList exception:\n" + str(e)

    def __uploadCuesheet__(self):
        try:
            seek = self.session.nav.getCurrentService().seek()
            if seek is None:
                print "upload failed, no seek interface"
                return
            self.modifyCutListEnries()
            writeCutList(self.currentService.getPath(), self.cut_list)
        except Exception, e:
            print "uploadCutList exception:\n" + str(e)

    def modifyCutListEnries(self):
        seek = self.session.nav.getCurrentService().seek()
        if seek is None:
            return
        stopPosition = seek.getPlayPosition()[1]
        length = seek.getLength()[1]
        if(stopPosition > length):
            stopPosition = 0
        
        if self.cut_list is not None:
            inList = False
            endInList = False
            for index, item in enumerate(self.cut_list):
                if item[1] == self.CUT_TYPE_LAST:
                    self.cut_list[index] = (stopPosition, self.CUT_TYPE_LAST)
                    inList = True
                if item[1] == self.CUT_TYPE_OUT:
                    self.cut_list[index] = (length, self.CUT_TYPE_OUT)
                    endInList = True
            if not inList:
                self.cut_list.append((stopPosition, self.CUT_TYPE_LAST))
            if not endInList:
                self.cut_list.append((length, self.CUT_TYPE_OUT))
        else:
            self.cut_list = [(stopPosition, self.CUT_TYPE_LAST)]
            self.cut_list.append((length, self.CUT_TYPE_OUT))
        
    def getCuePositions(self):
        length = 0
        last_pos = 0
        for (pts, what) in self.cut_list:
            if what == 1 == self.CUT_TYPE_OUT:
                length = pts / 90000
            if what == self.CUT_TYPE_LAST:
                last_pos = pts / 90000
        if length == 0:
            info = ServiceCenter.getInstance().info(self.currentService)
            if info:
                length = info.getLength(self.currentService)
        return [length, last_pos]

    def addPlayerEvents(self):
        try:
            self.onClose.insert(0, self.playerClosed)
        except Exception, e:
            print "addPlayerEvents exception: " + str(e)

    def playerClosed(self, service=None):
        try:
            cancel_cutlist = ["ts", "m4a", "mp3", "ogg", "wav"]
            ext = self.currentService.getPath().split(".")[-1].lower()
            if ext in cancel_cutlist:
                if service:
                    self.currentService = service
                return
            self.modifyCutListEnries()
            writeCutList(self.currentService.getPath(), self.cut_list)
            if service:
                self.currentService = service
        except Exception, e:
            print "playerClosed exception:\n" + str(e)

    def getDVDNameFromFile(self, file_name):
        if os.path.isfile(file_name):
            return os.path.basename(os.path.splitext(file_name)[0])
        else:
            return os.path.basename(file_name)

    def copyDVDCutsFromRoot(self):
        try:
            file_name = self.currentService.getPath()
            name = self.getDVDNameFromFile(file_name)
            src = "/home/root/dvd-%s.cuts" % (name.upper())
            dst = file_name + ".cuts"
            if os.path.exists(src):
                copyfile(src, dst)
        except Exception, e:
            print "copyDVDCutsFromRoot exception:\n" + str(e)

    def copyDVDCutsToRoot(self):
        try:
            file_name = self.currentService.getPath()
            src = file_name + ".cuts"
            if os.path.exists(src) and checkDVDCuts(file_name):
                name = self.getDVDNameFromFile(file_name)
                dst = "/home/root/dvd-%s.cuts" % (name.upper()) 
                copyfile(src, dst)
        except Exception, e:
            print "copyDVDCutsToRoot exception:\n" + str(e)

    def jumpToFirstMark(self):
        firstMark = None
        for (pts, what) in self.cut_list:
            if what == self.CUT_TYPE_MARK:
                firstMark = pts
                current_pos = self.cueGetCurrentPosition()
                #increase current_pos by 2 seconds to make sure we get the correct mark
                current_pos = current_pos + 180000
                if firstMark == None or current_pos < firstMark:
                    break
        if firstMark is not None:
            self.doSeek(firstMark)

    def playLastCB(self, answer):
        if answer == False and config.AdvancedMovieSelection.jump_first_mark.value == True:
            self.jumpToFirstMark()
        InfoBarCueSheetSupport.playLastCB(self, answer)
