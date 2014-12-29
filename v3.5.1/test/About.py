#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 09.03.2012

@author: cmikula

Source for parsing changes. 
'''

import AboutParser

def printAbout(lng="en"):
    AboutParser.setLocale(lng, "../src/")
    versions = AboutParser.parseChanges()
    for version in versions:
        print version.getVersion()
        print version.getInfo()

if __name__ == '__main__':
    printAbout("en")
    printAbout("de")
    printAbout("nl")
    printAbout("xyz")
    