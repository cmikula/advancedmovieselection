#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  The plugin is developed on the basis from a lot of single plugins (thx for the code @ all)
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
from __init__ import _
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MovieList import MovieList
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.MultiContent import MultiContentEntryText
from enigma import eServiceReference, eListboxPythonMultiContent, eListbox, eServiceCenter, gFont, iServiceInformation, eServiceReference, getDesktop
from Tools.Directories import *

class MovieTags(Screen):
    currList = None
    pretagfile = "/etc/enigma2/movietags"
    def __init__(self, session, service):
        Screen.__init__(self, session)
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            self.skinName = ["AdvancedMovieSelectionMovieTagsHD"]
        elif sz_w == 1024:
            self.skinName = ["AdvancedMovieSelectionMovieTagsXD"]
        else:
            self.skinName = ["AdvancedMovieSelectionMovieTagsSD"]
        self.session = session
        self.service = service
        self.serviceHandler = eServiceCenter.getInstance()
        self.info = self.serviceHandler.info(self.service)

        self["moviename"] = Label(_("Moviename:") + ' ' + self.info.getName(self.service))
        self["assignedTags"] = Label("AssignedTags")
        self["definedTags"] = Label("DefinedTags")
        self["usedTag"] = Label("UsedTag")
        self["userTag"] = Label("UserTag")
        self["preTag"] = Label("PreTag")
        self["buttonred"] = Label("red")
        self["buttongreen"] = Label("green")
        self["buttonyellow"] = Label("yellow")
        self["buttonblue"] = Label("blue")
        self["cTaglist"] = MenuList([])
        self["aTaglist"] = TagMenuList([])
        self["actions"] = ActionMap(["WizardActions","MenuActions","ShortcutActions"],
            {
            "back":     self.close,
            "red":         self.keyRed,
            "green":     self.keyGreen,
            "yellow":     self.keyYellow,
            "blue":     self.keyBlue,
            "up":         self.up,
            "down":     self.down,
            "left":     self.left,
            "right":     self.right,
            }, -1)
        self.loadPreTags()
        self.updateCurrentTagList()
        self.updateAllTagList()
        self.currList = self["aTaglist"]
        self.onLayoutFinish.append(self.keyBlue)

    def loadPreTags(self):
        if pathExists(self.pretagfile):
            fp = open(self.pretagfile,"r")
            t = fp.read()
            fp.close()
            self.pretags = t.replace("\n"," ").strip().split(" ")
            self.pretags.sort()
            print "pretags loaded ", self.pretags
        else:
            print "pretagsfile",self.pretagfile," does not exists"
            self.pretags = []

    def updateCurrentTagList(self):
        print "updating cTagList"
        self.serviceHandler = eServiceCenter.getInstance()
        self.info = self.serviceHandler.info(self.service)
        self.tags = self.info.getInfoString(self.service, iServiceInformation.sTags).split(' ')
        self.tags.sort()
        self["cTaglist"].l.setList(self.tags)

    def updateAllTagList(self):
        root = eServiceReference("2:0:1:0:0:0:0:0:0:0:" + resolveFilename(SCOPE_HDD))
        ml = MovieList(root)
        ml.load(root,None)
        xtmp = []
        xtmp.extend(ml.tags)
        self.usedTags = xtmp

        e = []+self.pretags
        for i in ml.tags:
            try:
                self.pretags.index(i)
            except ValueError:
                e.append(i)

        taglist = []
        for i in e:
            res = [ i ]
            res.append(MultiContentEntryText(pos=(5,0),size=(500,25),font=0,text=i))
            if self.isUsedTag(i):
                res.append(MultiContentEntryText(pos=(220,0),size=(20,25),font=1,text="X",color=0x00FFFF00)) #yellow
            if self.isUserTag(i) :
                res.append(MultiContentEntryText(pos=(240,0),size=(20,25),font=1, text="X",color=0x00FF0000)) #red
            if self.isPreTag(i):
                res.append(MultiContentEntryText(pos=(260,0),size=(20,25),font=1,text="X",color=0x0000FF00)) #green

            taglist.append(res)

        taglist.sort()
        self["aTaglist"].l.setList(taglist)

    def addTag(self,tagname):
        try:
            self.tags.index(tagname)
        except ValueError:
            self.tags.append(tagname)
            if len(self.tags) >1:
                self.setTags(" ".join(self.tags))
            else:
                self.setTags(tagname)
        self.updateCurrentTagList()
        self.updateAllTagList()


    def removeTag(self,tagname):
        newtags = []
        for i in self.tags:
            if i is not tagname:
                newtags.append(i)
        self.setTags(" ".join(newtags))
        self.updateCurrentTagList()
        self.updateAllTagList()


    def setTags(self,tagstring,service=False,userNotice=True):
        if service is False:
            serviceRef = self.service
        else:
            serviceRef = service

        service_name =serviceRef.toString().split(":")[-1]
        filename = service_name+".meta"
        metadata = self.readMETAData(filename)
        if metadata is not False:
            metadata.append(tagstring.strip())
            return  self.writeMETAData(filename,metadata)
        else:
            if userNotice is True:
                self.session.open(MessageBox,_("Can't write movietags, because no meta-file found!"), MessageBox.TYPE_ERROR)
            return  False


    def readMETAData(self,filename):
        if pathExists(filename):
            fp = open(filename,"r")
            data = []
            data.append(fp.readline())
            data.append(fp.readline())
            data.append(fp.readline())
            data.append(fp.readline())
            fp.close()
            return data
        else:
            return False
    def writeMETAData(self,filename,metadata):
        if pathExists(filename):
            fp = open(filename,"w")
            fp.write(metadata[0])
            fp.write(metadata[1])
            fp.write(metadata[2])
            fp.write(metadata[3])
            fp.write(metadata[4])
            fp.close()
            return True
        else:
            return False

    def clearAllTags(self,yesno):
        if yesno is True:
            self.serviceHandler = eServiceCenter.getInstance()
            root = eServiceReference("2:0:1:0:0:0:0:0:0:0:" + resolveFilename(SCOPE_HDD))
            list = self.serviceHandler.list(root)
            tags = set()
            if list is None:
                pass
            else:
                while 1:
                    serviceref = list.getNext()
                    if not serviceref.valid():
                        break
                    if serviceref.flags & eServiceReference.mustDescent:
                        continue
                    self.setTags("",service=serviceref,userNotice=False)
        self.updateCurrentTagList()
        self.updateAllTagList()

    def isUsedTag(self,tag):
        try:
            self.usedTags.index(tag)
            return True
        except ValueError:
            return False

    def isPreTag(self,tag):
        try:
            self.pretags.index(tag)
            return True
        except ValueError:
            return False

    def isUserTag(self,tag):
        if self.isPreTag(tag) is False and self.isUsedTag(tag) is True:
            return True
        else:
            return False

    def keyRed(self):
        if self.currList is self["cTaglist"]:
            self.removeTag(self["cTaglist"].getCurrent())

        elif self.currList is self["aTaglist"]:
            print "adding Tag",self["aTaglist"].getCurrent()[0]
            self.addTag(self["aTaglist"].getCurrent()[0])

    def keyGreen(self):
        if self.currList is self["cTaglist"]:
            self.session.openWithCallback(self.newTagEntered,InputBox, title=_('Whitepace will be replaced by "_"'),windowTitle = _("Enter the new Tag"))

    def keyYellow(self):
        if  self.currList is self["aTaglist"]:
            self.session.openWithCallback(self.clearAllTags,MessageBox,_("Clear all Tags?\n\nThis will delete ALL tags in ALL recodings!\nAre you sure?"), MessageBox.TYPE_YESNO)

    def keyBlue(self):
        self.setTitle(_("Set movie tags"))
        self["assignedTags"].setText(_("Assigned Tags"))
        self["definedTags"].setText(_("Specified Tags"))
        self["usedTag"].setText(_("Used Tag"))
        self["userTag"].setText(_("User-specific Tag"))
        self["preTag"].setText(_("Predefined Tag"))
        if self.currList is self["aTaglist"] or self.currList is None:
            self["aTaglist"].selectionEnabled(0)
            self["cTaglist"].selectionEnabled(1)
            self["buttonred"].setText(_("Remove Tag"))
            self["buttongreen"].setText(_("Create new Tag"))
            self["buttonyellow"].setText("")
            self["buttonblue"].setText(_("Toggle List"))
            self.currList = self["cTaglist"]
        else:
            self["aTaglist"].selectionEnabled(1)
            self["cTaglist"].selectionEnabled(0)
            self["buttonred"].setText(_("Add Tag"))
            self["buttongreen"].setText("")
            self["buttonyellow"].setText(_("Clear all Tags"))
            self["buttonblue"].setText(_("Toggle List"))
            self.currList = self["aTaglist"]

    def up(self):
        self.currList.up()

    def down(self):
        self.currList.down()

    def left(self):
        self.currList.pageUp()

    def right(self):
        self.currList.pageDown()

    def newTagEntered(self,newTag):
        if newTag >=0:
            self.addTag(newTag.strip().replace(" ","_"))

class TagMenuList(MenuList):
    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setFont(0, gFont("Regular", 20))
        self.l.setFont(1, gFont("Regular", 25))

    def postWidgetCreate(self, instance):
        MenuList.postWidgetCreate(self, instance)
        instance.setItemHeight(25)