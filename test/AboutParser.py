#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 09.03.2012

@author: cmikula

Source for parsing changes. 
'''

#CHANGES_PATH = "changes_de.txt"
CHANGES_PATH = "../src/changes_de.txt"

class VersionInfo():
    def __init__(self, version="", info=""):
        self.version = version
        self.info = info
    
    def getVersion(self):
        return self.version
    
    def getInfo(self):
        return self.info
    
    def __repr__(self):
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
    
if __name__ == '__main__':
    versions = parseChanges()
    for version in versions:
        print version.getVersion()
        print version.getInfo()
