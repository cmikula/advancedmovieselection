#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  Coded by cmikula & JackDaniel (c)2012
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
CHANGES_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/AdvancedMovieSelection/changes_de.txt"

class VersionInfo():
    def __init__(self, version="", info=""):
        self.version = version
        self.info = info
    
    def getVersion(self):
        return self.version
    
    def getInfo(self):
        return self.info
    
    def getTotal(self):
        return self.version + self.info 

def parseChanges():
    versions = []
    version = None
    for line in open(CHANGES_PATH, 'r').readlines():
        if not line:
            break
        if line.lower().startswith('version'):
            version = VersionInfo(line)
            versions.append(version)
        else:
            if not line.startswith(' ') and version:
                version.info += line
    return versions
