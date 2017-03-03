#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  Coded by cmikula (c)2013
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
from Globals import printStackTrace
from MovieConfig import MovieConfig
from ServiceProvider import eServiceReferenceHotplug
from Timer import xTimer

try:
    from Components.Harddisk import BlockDevice, Util #@UnresolvedImport
except:
    from os import path
    class Util:
        @staticmethod
        def readFile(filename):
            try:
                return file(filename).read().strip()
            except:
                print "Failed to read %s" % filename
    
        @staticmethod
        def __capacityStringDiv(cap, divisor, unit):
            if cap < divisor:
                return ""
            value = cap * 10 / divisor
            remainder = value % 10
            value /= 10
            # Return at most one decimal place, but no leading zero.
            if remainder == 0:
                return "%d %s" % (value, unit)
            return "%d.%d %s" % (value, remainder, unit)
    
        @staticmethod
        def capacityString(cap):
            return (Util.__capacityStringDiv(cap, 1000000000000, 'PB') or
                Util.__capacityStringDiv(cap, 1000000000, 'TB') or
                Util.__capacityStringDiv(cap, 1000000, 'GB') or
                Util.__capacityStringDiv(cap, 1000, 'MB') or
                Util.__capacityStringDiv(cap, 1, 'KB'))

    
    class BlockDevice:
        def __init__(self, devname):
            self._name = path.basename(devname)
            self._blockPath = path.join('/sys/block', self._name)
            self._classPath = path.realpath(path.join('/sys/class/block', self._name))
            self._deviceNode = devname
            try:
                self._partition = int(Util.readFile(self.sysfsPath('partition')))
            except:
                self._partition = 0
            try:
                # Partitions don't have a 'removable' property. Ask their parent.
                self._isRemovable = bool(int(Util.readFile(self.sysfsPath('removable', physdev=True))))
            except IOError:
                self._isRemovable = False
    
        def capacityString(self):
            return Util.capacityString(self.size())
    
        def name(self):
            return self._name
    
        def partition(self):
            return self._partition
    
        def isRemovable(self):
            return self._isRemovable
    
        def hasMedium(self):
            if self._isRemovable:
                try:
                    open(self._deviceNode, 'rb').close()
                except IOError, err:
                    if err.errno == 159: # no medium present
                        return False
            return True
    
        def sectors(self):
            try:
                return int(Util.readFile(self.sysfsPath('size')))
            except:
                return 0
    
        def size(self):
            # Assume 512-bytes sectors, even for 4K drives. Return KB.
            return self.sectors() * 512 / 1000
    
        def sysfsPath(self, filename, physdev=False):
            classPath = self._classPath
            if physdev and self._partition:
                classPath = path.dirname(classPath)
            return path.join(classPath, filename)


class Hotplug():
    NTFS_3G_DRIVER_DELAY = 3000
    def __init__(self):
        self.notifier = []
        self.hotplugServices = []
        self.hotplug_timer = xTimer()
        self.hotplug_timer.addCallback(self.updateHotplugDevices)
        self.addHotplugNotifier()
        self.hotplugChanged()

    def addHotplugNotifier(self):
        from Plugins.SystemPlugins.Hotplug.plugin import hotplugNotifier
        print "add hotplugNotifier" 
        hotplugNotifier.append(self.hotplugNotifier)
        
    def removeHotplugNotifier(self):
        from Plugins.SystemPlugins.Hotplug.plugin import hotplugNotifier
        print "remove hotplugNotifier" 
        hotplugNotifier.remove(self.hotplugNotifier)
    
    def hotplugNotifier(self, dev, media_state):
        print "[hotplugNotifier]", dev, media_state
        if len(dev) > 2 and dev[0:2] in ("sd") and dev[-1].isdigit():
            if media_state == "add":
                self.hotplugChanged(self.NTFS_3G_DRIVER_DELAY)
            else:
                self.hotplugChanged(200)

    def hotplugChanged(self, delay=200):
        print "[start hotplugNotifier]", str(delay) + "ms"
        self.hotplug_timer.start(delay, True)

    def updateHotplugDevices(self):
        self.hotplugServices = []
        print "[update hutplug]"
        try:
            import commands
            movieConfig = MovieConfig()
            lines = commands.getoutput('mount | grep /dev/sd').split('\n')
            print lines
            for mount in lines:
                if len(mount) < 2:
                    continue
                dev = mount.split(' on ')[0].strip()
                m = mount.split(' type')[0].split(' on ')
                m_dev, m_path = m[0], m[1]
                label = os.path.split(m_path)[-1]
                blkid = commands.getoutput('blkid ' + m_dev).split("\"")
                if len(blkid) > 2 and blkid[1]:
                    label = blkid[1]
                if os.path.normpath(m_path) == "/media/hdd" or label in ("DUMBO", "TIMOTHY"):
                    continue
                if not movieConfig.isHiddenHotplug(label):
                    blkdev = BlockDevice(dev)
                    if m_path[-1] != "/":
                        m_path += "/"
                    
                    #print blkdev.isRemovable()
                    #print blkdev.name()
                    #print blkdev.capacityString()
                    if not blkdev.isRemovable():
                        continue
                    
                    service = eServiceReferenceHotplug(m_path)
                    devname = m_dev.replace("/dev/", "")[:-1]
                    filename = str.format("/sys/block/{0}/device/block/{0}/device/model", devname)
                    #model = commands.getoutput("cat " + filename)
                    model = Util.readFile(filename)
                    if label:
                        label += " - "
                    service.setName(label + model + " - " + blkdev.capacityString())
                    self.hotplugServices.append(service)
            
            for callback in self.notifier:
                try:
                    callback()
                except:
                    printStackTrace()
        except:
            printStackTrace()
    
    def getHotplugServices(self):
        return self.hotplugServices


hotplug = Hotplug()
