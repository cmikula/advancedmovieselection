#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 09.03.2012

@author: cmikula

Source for parsing changes. 
'''

import AboutParser

if __name__ == '__main__':
    AboutParser.setLocale("en", "../src/")
    versions = AboutParser.parseChanges()
    for version in versions:
        print version.getVersion()
        print version.getInfo()
    AboutParser.setLocale("de", "../src/")
    versions = AboutParser.parseChanges()
    for version in versions:
        print version.getVersion()
        print version.getInfo()
    AboutParser.setLocale("nl", "../src/")
    versions = AboutParser.parseChanges()
    for version in versions:
        print version.getVersion()
        print version.getInfo()
