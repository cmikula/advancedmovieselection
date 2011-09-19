#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Renderer for AdvancedMovieSelection plugin
#
#  Coded by JackDaniel (c)2011
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
from Renderer import Renderer
from enigma import ePixmap, eEnv
from Tools.Directories import fileExists, SCOPE_PLUGINS, resolveFilename

class AdvancedMovieSelectionPicon(Renderer):
    searchPaths = (eEnv.resolve('${datadir}/enigma2/%s/'), '/media/cf/%s/', '/media/usb/%s/')
    def __init__(self):
        Renderer.__init__(self)
        self.path = "picon"
        self.nameCache = { }
        self.pngname = ""

    def applySkin(self, desktop, parent):
        attribs = [ ]
        for (attrib, value) in self.skinAttributes:
            if attrib == "path":
                self.path = value
            else:
                attribs.append((attrib,value))
        self.skinAttributes = attribs
        return Renderer.applySkin(self, desktop, parent)

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if self.instance:
            pngname = ""
            if what[0] != self.CHANGED_CLEAR:
                sname = self.source.text
                # strip all after last :
                pos = sname.rfind(':')
                if pos != -1:
                    sname = sname[:pos].rstrip(':').replace(':','_')
                pngname = self.nameCache.get(sname, "")
                if pngname == "":
                    pngname = self.findPicon(sname)
                    if pngname != "":
                        self.nameCache[sname] = pngname
            if pngname == "": # no picon for service found
                pngname = self.nameCache.get("default", "")
                if pngname == "": # no default yet in cache..
                    pngname = self.findPicon("providerlogo_default")
                    if pngname == "":
                        tmp = resolveFilename(SCOPE_PLUGINS, "Extensions/AdvancedMovieSelection/skin/providerlogo_default.png")
                        if fileExists(tmp):
                            pngname = tmp
                    self.nameCache["default"] = pngname
            if self.pngname != pngname:
                self.instance.setPixmapFromFile(pngname)
                self.pngname = pngname

    def findPicon(self, serviceName):
        for path in self.searchPaths:
            pngname = (path % self.path) + serviceName + ".png"
            if fileExists(pngname):
                return pngname
        return ""
