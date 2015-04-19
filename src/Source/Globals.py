#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  The plugin is developed on the basis from a lot of single plugins (thx for the code @ all)
#  Coded by JackDaniel and cmikula (c)2012
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
from enigma import getDesktop
from Tools.Directories import fileExists, resolveFilename, SCOPE_CURRENT_PLUGIN, SCOPE_CURRENT_SKIN
from Components.config import config

try:
    from enigma import eMediaDatabase
    isDreamOS = True
except:
    isDreamOS = False


IMAGE_PATH = "Extensions/AdvancedMovieSelection/images/"

def getIconPath(png_name):
    p = resolveFilename(SCOPE_CURRENT_SKIN, "extensions/" + png_name)
    if config.AdvancedMovieSelection.showskinicons.value or not fileExists(p):
        p = p = resolveFilename(SCOPE_CURRENT_PLUGIN, IMAGE_PATH + png_name)
    return p


def printStackTrace():
    import sys, traceback
    print "--- [AdvancedMovieSelection] STACK TRACE ---"
    traceback.print_exc(file=sys.stdout)
    print '-' * 50

class SkinTools():
    DESKTOP_WIDTH_SD = 720
    DESKTOP_WIDTH_XD = 1024
    DESKTOP_WIDTH_HD = 1280
    DESKTOP_WIDTH_FHD = 1920
    def __init__(self):
        pass

    @staticmethod
    def getSkinName():
        dw = SkinTools.getDesktopWidth()
        #if dw == SkinTools.DESKTOP_WIDTH_FHD:
        #    return "1920.xml"
        if dw == SkinTools.DESKTOP_WIDTH_XD:
            return "1024.xml"
        elif dw == SkinTools.DESKTOP_WIDTH_SD:
            return "720.xml"
        return "1280.xml"
    
    @staticmethod
    def getDesktopWidth():
        try:
            desktopWidth = getDesktop(0).size().width()
        except:
            desktopWidth = SkinTools.DESKTOP_WIDTH_SD
        return desktopWidth
    
    @staticmethod
    def insertBackdrop(skinName):
        bdl = []
        for sn in skinName:
            bdl.insert(0, sn + "_Backdrop")
        for sn in bdl:
            skinName.insert(0, sn)


class Installed:
    def __init__(self):
        self.GP3 = resolveFilename(SCOPE_CURRENT_PLUGIN, "Bp/geminimain/plugin.pyo")
        self.BludiscPlayer = self.pluginInstalled("BludiscPlayer")
        self.DVDPlayer = self.pluginInstalled("DVDPlayer")
        self.TMDb = self.pluginInstalled("TMDb")
        self.IMDb = self.pluginInstalled("IMDb")
        self.OFDb = self.pluginInstalled("OFDb")
        self.TheTVDB = self.pluginInstalled("TheTVDB")
        self.AdvancedProgramGuide = self.pluginInstalled("AdvancedProgramGuide")
        self.MerlinEPG = self.pluginInstalled("MerlinEPG")
        self.MerlinEPGCenter = self.pluginInstalled("MerlinEPGCenter")
        self.CoolTVGuide = self.pluginInstalled("CoolTVGuide")
        self.YTTrailer = self.pluginInstalled("YTTrailer")
        self.pipzap = self.pluginInstalled("pipzap")
    
    def pluginInstalled(self, name):
        plugin_path = resolveFilename(SCOPE_CURRENT_PLUGIN, "Extensions/%s/plugin.pyo" % (name))
        return fileExists(plugin_path)


pluginPresent = Installed()
