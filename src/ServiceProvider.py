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
from Tools.Directories import resolveFilename, SCOPE_CURRENT_PLUGIN, SCOPE_CONFIG
from EventInformationTable import EventInformationTable
from Components.config import config
from Screens.InfoBarGenerics import InfoBarCueSheetSupport
import struct
import os
from shutil import copyfile
from Components.AVSwitch import AVSwitch
from enigma import ePicLoad
import ping
from bisect import insort

def cutlist_changed(self):
    from MoviePlayer import PlayerInstance
    if PlayerInstance:
        self.cutlist = [] # we need to update the property 
    self.cutlist = self.source.cutlist or [ ]

from Components.Renderer.PositionGauge import PositionGauge
PositionGauge.cutlist_changed = cutlist_changed

if fileExists(resolveFilename(SCOPE_CURRENT_PLUGIN, "Bp/geminimain/plugin.pyo")):
    __CONF__ = resolveFilename(SCOPE_CONFIG, "gemini_DateiBrowser.conf")
else:
    __CONF__ = resolveFilename(SCOPE_CONFIG, "AdvancedMovieSelection.conf")

if not fileExists(__CONF__):
    copyfile(resolveFilename(SCOPE_CURRENT_PLUGIN, "Extensions/AdvancedMovieSelection/AdvancedMovieSelection.conf"), __CONF__)
DMCONFFILE = __CONF__

instance = None
auto_network = []
AUTO_NETORK = "/etc/auto.network"

def printStackTrace():
    import sys, traceback
    print "--- [AdvancedMovieSelection] print stack trace ---"
    print '-' * 50
    traceback.print_exc(file=sys.stdout)
    print '-' * 50

def getServiceInfoValue(ref, what):
    # only works with ts files, if necessary use the ServiceCenter class
    info = eServiceCenter.getInstance().info(ref)
    v = ref and info.getInfo(ref, what) or info.getInfo(what)
    if v != iServiceInformation.resIsString:
        return ""
    return ref and info.getInfoString(ref, what) or info.getInfoString(what)

class PicLoader:
    def __init__(self, width, height, sc=None):
        self.picload = ePicLoad()
        if(not sc):
            sc = AVSwitch().getFramebufferScale()
        self.picload.setPara((width, height, sc[0], sc[1], False, 1, "#00000000"))

    def load(self, filename):
        self.picload.startDecode(filename, 0, 0, False)
        data = self.picload.getData()
        return data
    
    def destroy(self):
        del self.picload

class eServiceReferenceBludisc(eServiceReference):
    def __init__(self, serviceref, isStruct=False):
        idx = 0
        eServiceReference.__init__(self, 4369, 0, serviceref.getPath())
        #eServiceReference.__init__(self, 0x04, 0, "%s:%03d" % (serviceref.getPath(), idx))
        self.isStruct = isStruct
        if isStruct is True:
            # remove trailing slash
            self.setPath(serviceref.getPath()[0:-1])
            self.setName(os.path.basename(self.getPath()))
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
        eServiceReference.__init__(self, 4369, 0, serviceref.getPath())
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
        
    def isIsoImage(self):
        return not self.dvdStruct

import commands
class ISOInfo():
    ERROR = -1
    UNKNOWN = 0
    DVD = 1
    BLUDISC = 2
    MOUNT_PATH = "/media/bludisc.iso"
    def __init__(self):
        pass
    
    def getFormat(self, service):
        print "checking iso:", service.getPath()
        if not self.mount(service.getPath()):
            return self.ERROR 
        if os.path.exists(self.MOUNT_PATH + "/BDMV/"):
            print "Bludisc iso file detected"
            return self.BLUDISC
        if os.path.exists(self.MOUNT_PATH + "/VIDEO_TS/") or os.path.exists(self.MOUNT_PATH + "/VIDEO_TS.IFO"):
            print "DVD iso file detected"
            self.umount()
            return self.DVD
        print "Unknown iso file"
        return self.UNKNOWN

    def getFormatISO9660(self, service):
        #if os.path.exists(iso):
        #    print True
        print "checking iso:", service.getPath()
        cmd = "isoinfo -p -i \"%s\"" % (service.getPath())
        dirs = os.popen(cmd)
        for d in dirs.readlines():
            if "BDMV" in d:
                print "Bludisc iso file detected"
                return self.BLUDISC
            elif "VIDEO_TS" in d:
                print "DVD iso file detected"
                return self.DVD
        print "Unknown iso file"
        return self.UNKNOWN
    
    def mount(self, iso):
        self.umount()
        try:
            if not os.path.exists(self.MOUNT_PATH):
                print "Creating mount path for bludisc iso on:", self.MOUNT_PATH
                os.mkdir(self.MOUNT_PATH)
            cmd = "mount -r -o loop \"%s\" \"%s\"" % (iso, self.MOUNT_PATH)
            print "exec command:", cmd
            out = commands.getoutput(cmd)
            if out:
                print "error:", out
            return not out
        except:
            printStackTrace()
            return False

    @classmethod
    def umount(self):
        try:
            cmd = "umount -df \"%s\"" % (ISOInfo.MOUNT_PATH)
            print "exec command:", cmd
            out = commands.getoutput(cmd)
            if out:
                print "error:", out
            return not out
        except:
            printStackTrace()
            return False
    
    def getPath(self):
        return self.MOUNT_PATH
    
    def getService(self, service):
        service = eServiceReferenceBludisc(service)
        service.setBludisc(self.MOUNT_PATH)
        return service

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


class Network():
    @staticmethod
    def isMountOnline(mount_dir):
        try:
            if mount_dir == "/":
                return True
            for network in auto_network:
                if network[0] in mount_dir:
                    delay = ping.do_one(network[1], 0.2)
                    if delay:
                        return True
                    else:
                        return False
            return True
        except:
            return True
    
    @staticmethod
    def updateAutoNetwork():
        global auto_network
        auto_network = []
        try:
            if os.path.exists(AUTO_NETORK): 
                rfile = open(AUTO_NETORK, 'r')
                for x in rfile.readlines():
                    val = x.strip().split(' ')
                    if len(val) >= 2 and not '#' in val[0]:
                        val[2] = val[2].replace('://', '').replace(':/', '/', 1) # only for cifs mount
                        dest_addr = val[2].split('/')[0]
                        auto_network.append((val[0], dest_addr))
        except Exception, e:
            print e

def getFolderSize(loadPath):
    folder_size = 0
    try:
        for (path, dirs, files) in os.walk(loadPath):
            for file in files:    
                filename = os.path.join(path, file)    
                if os.path.exists(filename):
                    folder_size += os.path.getsize(filename)
    except Exception, e:
        print e
    return folder_size

def getDirSize(root):
    folder_size = 0
    try:
        for filename in os.listdir(root):
            p = os.path.join(root, filename)
            if os.path.exists(p):
                folder_size += os.path.getsize(p)
    except Exception, e:
        print e
    return folder_size

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
        print "ERROR writing cutlist", fileName + ".cuts:", e
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
            cutList.append((long(where), what))
    except Exception, e:
        print "ERROR reading cutlist", fileName + ".cuts:", e
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
        metafile.write("%s\n%s\n%s\n%s\n%s\n" % (sid, title, descr, time, tags))
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


class CutListSupportBase:
    def __init__(self, service):
        self.currentService = service
        self.cut_list = [ ]
        self.resume_point = 0
        self.jump_first_mark = None
        self.jump_first_play_last = None
        self.currently_playing = False

    def getCuesheet(self):
        service = self.session.nav.getCurrentService()
        if service is None:
            return None
        cue = service.cueSheet()
        if cue:
            return cue
        else:
            cue = CueSheet(self.currentService)
            self.session.nav.currentlyPlayingService.cueSheet = cue
            return cue

    def checkResumeSupport(self):
        self.jump_first_mark = None
        self.jump_first_play_last = None
        stop_before_end_time = int(config.AdvancedMovieSelection.stop_before_end_time.value)
        length, last = self.getCuePositions()  
        if stop_before_end_time > 0:
            if ((length - last) / 60) < stop_before_end_time or length < last:
                self.ENABLE_RESUME_SUPPORT = False
            else:
                self.ENABLE_RESUME_SUPPORT = True
        if config.AdvancedMovieSelection.jump_first_mark.value == True:
            first = self.getFirstMark()
            if (first and length > 0) and (first / 90000) < length / 2:
                self.jump_first_play_last = first
                if not hasLastPosition(self.currentService):
                    self.ENABLE_RESUME_SUPPORT = False
                    self.jump_first_mark = self.resume_point = first

    def getFirstMark(self):
        firstMark = None
        for (pts, what) in self.cut_list:
            if what == self.CUT_TYPE_MARK:
                if not firstMark:
                    firstMark = pts
                elif pts < firstMark:
                    firstMark = pts
        return firstMark

    def downloadCuesheet(self):
        try:
            self.currently_playing = True
            cue = self.getCuesheet()
            if cue is None:
                print "download failed, no cuesheet interface! Try to load from cuts"
                self.cut_list = [ ]
                if self.currentService is not None:
                    self.cut_list = getCutList(self.currentService.getPath())
            else:
                self.cut_list = cue.getCutList()
            print self.cut_list
            self.checkResumeSupport()
            if self.jump_first_mark:
                self.doSeek(self.resume_point)
        except Exception, e:
            print "DownloadCutList exception:\n" + str(e)

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
                insort(self.cut_list, (stopPosition, self.CUT_TYPE_LAST))
                #self.cut_list.append((stopPosition, self.CUT_TYPE_LAST))
            if not endInList:
                insort(self.cut_list, (length, self.CUT_TYPE_OUT))
                #self.cut_list.append((length, self.CUT_TYPE_OUT))
        else:
            self.cut_list = [(stopPosition, self.CUT_TYPE_LAST)]
            insort(self.cut_list, (length, self.CUT_TYPE_OUT))
            #self.cut_list.append((length, self.CUT_TYPE_OUT))
        
    def getCuePositions(self):
        length = 0
        last_pos = 0
        for (pts, what) in self.cut_list:
            if what == self.CUT_TYPE_OUT:
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
            self.currently_playing = False
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

    def isCurrentlyPlaying(self):
        return self.currently_playing

    def getDVDNameFromFile(self, file_name):
        if os.path.isfile(file_name):
            return os.path.basename(os.path.splitext(file_name)[0])
        else:
            return os.path.basename(file_name)

    def storeDVDCueSheet(self):
        try:
            file_name = self.currentService.getPath()
            name = self.getDVDNameFromFile(file_name)
            src = "/home/root/dvd-%s.cuts" % (name.upper())
            if os.path.isdir(file_name):
                src = os.path.join(file_name, "dvd.cuts")
            dst = file_name + ".cuts"
            if os.path.exists(src):
                copyfile(src, dst)
        except Exception, e:
            print "storeDVDCueSheet exception:\n" + e

    def loadDVDCueSheet(self):
        try:
            file_name = self.currentService.getPath()
            src = file_name + ".cuts"
            if os.path.exists(src) and os.path.isfile(file_name) and checkDVDCuts(file_name):
                name = self.getDVDNameFromFile(file_name)
                dst = "/home/root/dvd-%s.cuts" % (name.upper()) 
                copyfile(src, dst)
        except Exception, e:
            print "loadDVDCueSheet exception:\n" + e

class DVDCutListSupport(CutListSupportBase):
    def __init__(self, service):
        CutListSupportBase.__init__(self, service)
        self.jump_relative = False

    def downloadCuesheet(self):
        from Plugins.Extensions.DVDPlayer.plugin import DVDPlayer as eDVDPlayer
        eDVDPlayer.downloadCuesheet(self)
        if len(self.cut_list) == 0:
            self.cut_list = getCutList(self.currentService.getPath())
            self.jump_relative = True
        self.checkResumeSupport()
        if self.ENABLE_RESUME_SUPPORT == False:
            if self.jump_first_mark:
                eDVDPlayer.playLastCB(self, True)
            else:
                eDVDPlayer.playLastCB(self, False)

    def __getServiceName(self, service):
        try:
            from enigma import iPlayableServicePtr
            if isinstance(service, iPlayableServicePtr):
                info = service and service.info()
                ref = None
            else: # reference
                info = service and self.source.info
                ref = service
            if info is None:
                return "no info"
            name = ref and info.getName(ref)
            if name is None:
                name = info.getName()
            return name.replace('\xc2\x86', '').replace('\xc2\x87', '')
        except Exception, e:
            print e

    def playLastCB(self, answer): # overwrite infobar cuesheet function
        from Plugins.Extensions.DVDPlayer.plugin import DVDPlayer as eDVDPlayer
        if not self.jump_relative:
            eDVDPlayer.playLastCB(self, answer)
        else:
            if answer == True:
                eDVDPlayer.doSeekRelative(self, self.resume_point)
            eDVDPlayer.playLastCB(self, False)

class CutListSupport(CutListSupportBase):
    def __init__(self, service):
        CutListSupportBase.__init__(self, service)

    def playLastCB(self, answer):
        if answer == False and self.jump_first_play_last:
            self.resume_point = self.jump_first_play_last
            answer = True
        InfoBarCueSheetSupport.playLastCB(self, answer)

    def toggleMark(self, onlyremove=False, onlyadd=False, tolerance=5 * 90000, onlyreturn=False):
        if not self.currentService.getPath().endswith(".ts"):
            tolerance = 20 * 90000
        InfoBarCueSheetSupport.toggleMark(self, onlyremove=False, onlyadd=False, tolerance=tolerance, onlyreturn=False)

class BludiscCutListSupport(CutListSupport):
    def __init__(self, service):
        CutListSupportBase.__init__(self, service)

    def playerClosed(self, service=None):
        seek = self.session.nav.getCurrentService().seek()
        if seek is None:
            return
        #stopPosition = seek.getPlayPosition()[1]
        length = seek.getLength()[1]
        if length > 90000 * 60 * 5: # only write cutlist if length of movie > 5 minutes
            CutListSupportBase.playerClosed(self, service)

    def getCuesheet(self):
        service = self.session.nav.getCurrentService()
        if service is None:
            return None
        cue = service.cueSheet()
        cut_bd = cue.getCutList()
        cue = CueSheet(self.currentService)
        cut_hd = cue.getCutList()
        update_cue = False
        # add existing cuts from BludiscPlayer  
        if cut_bd and not (0L, 2) in cut_hd:
            for cut in cut_bd:
                if not cut in cut_hd:
                    print "add cut:", cut
                    insort(cut_hd, cut)
                    update_cue = True
        if update_cue:
            print "update cue"
            cue.setCutList(cut_hd)
        self.session.nav.currentlyPlayingService.cueSheet = cue
        return cue
