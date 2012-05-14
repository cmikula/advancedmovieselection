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
from enigma import eServiceReference, eSize, ePoint, eTimer, getDesktop
from Tools.Directories import fileExists, resolveFilename, SCOPE_HDD, SCOPE_CURRENT_SKIN, SCOPE_CURRENT_PLUGIN

class SkinTools():
    DESKTOP_WIDTH_SD = 720
    DESKTOP_WIDTH_XD = 1024
    DESKTOP_WIDTH_HD = 1280
    def __init__(self):
        pass
    
    @classmethod
    def parseScinName(self, skinName):
        dw = self.getDesktopWidth()
        if dw == self.DESKTOP_WIDTH_XD:
            return skinName + "XD"
        elif dw == self.DESKTOP_WIDTH_HD:
            return skinName + "HD"
        elif dw == self.DESKTOP_WIDTH_SD:
            return skinName + "SD"
        return skinName
    
    @classmethod
    def getDesktopWidth(self):
        try:
            desktopWidth = getDesktop(0).size().width()
        except:
            desktopWidth = self.DESKTOP_WIDTH_SD
        return desktopWidth

class Installed:
    def __init__(self):
        self.GP3 = resolveFilename(SCOPE_CURRENT_PLUGIN, "Bp/geminimain/plugin.pyo")
        self.DVDPlayer = self.pluginInstalled("DVDPlayer")
        self.TMDb = self.pluginInstalled("TMDb")
        self.IMDb = self.pluginInstalled("IMDb")
        self.OFDb = self.pluginInstalled("OFDb")
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
