#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  Coded by cmikula (c)2016
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
from enigma import eTimer as Timer
from Globals import isDreamOS

class eTimer():
    def __init__(self):
        self.__timer = Timer()
        self.__timer_conn = None
    
    def destroy(self):
        self.__timer.stop()
        self.__timer_conn = None
    
    def addCallback(self, callback):
        if isDreamOS:
            self.__timer_conn = self.__timer.timeout.connect(callback)
        else:
            self.__timer.callback.append(callback)
    
    def start(self, *args):
        return self.__timer.start(*args)
    
    def stop(self):
        return self.__timer.stop()
    
    def isActive(self):
        return self.__timer.isActive()
