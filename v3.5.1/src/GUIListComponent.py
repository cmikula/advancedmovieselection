#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  The plugin is developed on the basis from a lot of single plugins (thx for the code @ all)
#  Coded by and cmikula (c)2014
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
from Components.GUIComponent import GUIComponent
from enigma import eListbox, eListboxPythonMultiContent

class GUIListComponent(GUIComponent):
    def __init__(self):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.onSelectionChanged = [ ]

    def connectSelChanged(self, fnc):
        if not fnc in self.onSelectionChanged:
            self.onSelectionChanged.append(fnc)

    def disconnectSelChanged(self, fnc):
        if fnc in self.onSelectionChanged:
            self.onSelectionChanged.remove(fnc)

    def selectionChanged(self):
        for x in self.onSelectionChanged:
            x()        

    GUI_WIDGET = eListbox
    
    def postWidgetCreate(self, instance):
        instance.setContent(self.l)
        self.selectionChanged_conn = instance.selectionChanged.connect(self.selectionChanged)

    def preWidgetRemove(self, instance):
        instance.setContent(None)
        self.selectionChanged_conn = None

    def moveUp(self):
        self.instance.moveSelection(self.instance.moveUp)

    def moveDown(self):
        self.instance.moveSelection(self.instance.moveDown)
        
    def moveToIndex(self, index):
        self.instance.moveSelectionTo(index)

    def getCurrent(self):
        l = self.l.getCurrentSelection()
        return l and l[0]

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()
    
    def getSelectionIndex(self):
        return self.l.getCurrentSelectionIndex()

    def setList(self, l):
        self.l.setList(l)
    
