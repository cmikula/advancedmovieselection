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
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.LocationBox import MovieLocationBox
from enigma import eServiceCenter, iServiceInformation
from Screens.Console import Console as eConsoleAppContainer
from Components.config import config
from Components.UsageConfig import defaultMoviePath
from Tools.Directories import createDir
import os

class MovieMove(Screen):
    def __init__(self, session, service):
        self.session = session
        self.service = service
        Screen.__init__(self, session)
        serviceHandler = eServiceCenter.getInstance()
        info = serviceHandler.info(self.service)
        self.path = self.service.getPath()
        self.name = info.getName(self.service)
        self.descr = info.getInfoString(self.service, iServiceInformation.sDescription)
        self.filename = ""
        self.moviename = ""
        self.destinationpath = ""
        self.sourcepath = ""
        cbkeys = []
        listpath = [] 
        for element in range(len(listpath)):
            if element <= 10:
                cbkeys.append(str(element))
            else:
                cbkeys.append("")
        listpath.append((_("To adjusted move/copy location"), _("To adjusted move/copy location"), "", ""))
        cbkeys.append("blue")
        listpath.append((_("Directory Selection"), _("Directory Selection"), "", ""))
        cbkeys.append("yellow")
        listpath.append((_("Show active move/copy processes"), _("Show active move/copy processes"), "", ""))
        cbkeys.append("green")

        if len(os.listdir(config.movielist.last_videodir.value)) == 0 and defaultMoviePath() <> config.movielist.last_videodir.value:
            listpath.append((_("Remove ' %s '") % config.movielist.last_videodir.value, ("Verzeichnis entfernen ...", "", "")))
            cbkeys.append("red")
        self.session.openWithCallback(self.SelectPathConfirmed, ChoiceBox, title=(_("Where to ' %s ' are moved/copied ?") % (self.name)), list=listpath, keys=cbkeys)

    def SelectPathConfirmed(self, answer):
        if answer is not None:
            if answer[0] == _("To adjusted move/copy location"):
                self.gotFilename(config.AdvancedMovieSelection.movecopydirs.value)
            elif answer[0] == _("Directory Selection"):
                self.session.openWithCallback(self.gotFilename, MovieLocationBox, _("Please select the move/copy destination"), config.movielist.last_videodir.value)
            elif answer[0] == _("Show active move/copy processes"):
                tmp_out = os.popen("ps -ef | grep -e \"   [c]p /\" -e \"   [m]v /\"").readlines()
                tmpline = ""
                tmpcount = 0
                for line in tmp_out:
                    tmpcount = tmpcount + 1
                    tmpline = tmpline + "\n" + line.replace(" cp ", _("|Copy:\n"), 1).replace(" mv ", _("|Move:\n") , 1).split("|", 1)[1].rsplit(".", 1)[0]
                if tmpcount == 0:
                    self.session.open(MessageBox, _("There are currently no files are moved or copied."), MessageBox.TYPE_INFO, 5)
                elif tmpcount == 1:
                    self.session.open(MessageBox, (_("The following file is being moved or copied currently:\n%s") % tmpline), MessageBox.TYPE_INFO)
                else:
                    self.session.open(MessageBox, (_("The following %s files are being moved or copied currently:\n%s") % (str(tmpcount), tmpline)), MessageBox.TYPE_INFO)					
            elif answer[0] == (_("Remove ' %s '") % config.movielist.last_videodir.value):
                os.rmdir(config.movielist.last_videodir.value)
                self.gotFilename(defaultMoviePath())
            else:
                self.gotFilename(answer[1][2])
                                    
    def CreateConfirmedPath(self, DirToCreate):
        if DirToCreate is not None and DirToCreate <> "":
            if createDir(self.ParentDir + DirToCreate.strip()):
                MovieMove(session=self.session, service=self.service)
            else:
                self.session.openWithCallback(MovieMove(session=self.session, service=self.service), MessageBox, (_("The directory ' %s 'could not be created !") % (config.movielist.last_videodir.value + DirToCreate.lstrip())), MessageBox.TYPE_WARNING)
        else:
            MovieMove(session=self.session, service=self.service)	
            
    def gotFilename(self, destinationpath, retval=None):
        if destinationpath is None:
            self.skipMoveFile(_("Directory selection has been canceled"))
        else:
            self.filename = self.path.rsplit('/', 1)[1]
            self.moviename = self.filename.rsplit(".", 1)[0]
            self.destinationpath = destinationpath
            self.sourcepath = self.path.rsplit('/', 1)[0]
            listtmp = [(_("Move (in the background)"), "VH"), (_("Move (in the foreground)"), "VS"), (_("Copy (in the background)"), "KH"), (_("Copy (in the foreground)"), "KS"), (_("Abort"), "AB") ]
            self.session.openWithCallback(self.DoMove, ChoiceBox, title=(_("How to ' %s ' from %s to %s be moved/copied ?") % (self.name, self.sourcepath, self.destinationpath)), list=listtmp)
    
    def DoMove(self, confirmed):
        if confirmed is not None:
            if confirmed[1] <> "AB":
                if os.path.exists(self.destinationpath) is False:
                    os.system("mkdir %s" % self.destinationpath)
                if os.path.exists(self.destinationpath + "/%s" % self.filename) is True:
                    self.skipMoveFile(_("File already exists"))
                elif confirmed[1] == "VS":
                    os.system("mv \"%s/%s.\"* \"%s\"" % (self.sourcepath, self.moviename, self.destinationpath))
                    self.session.openWithCallback(self.DoneForeground, MessageBox, _("The move was successful."), MessageBox.TYPE_INFO, timeout=3)
                elif confirmed[1] == "VH":
                    self.container = eConsoleAppContainer()
                    self.container.execute("mv \"%s/%s.\"* \"%s\" &" % (self.sourcepath, self.moviename, self.destinationpath))
                    self.session.openWithCallback(self.DoneBackground, MessageBox, _("Moving in the background.\n\nThe movie list appears updated after full completion."), MessageBox.TYPE_INFO, timeout=12)
                elif confirmed[1] == "KS":
                    os.system("cp \"%s/%s.\"* \"%s\"" % (self.sourcepath, self.moviename, self.destinationpath))
                    self.session.openWithCallback(self.DoneForeground, MessageBox, _("The copying was successful."), MessageBox.TYPE_INFO, timeout=3)
                elif confirmed[1] == "KH":
                    os.system("cp \"%s/%s.\"* \"%s\" &" % (self.sourcepath, self.moviename, self.destinationpath))
                    self.session.openWithCallback(self.DoneBackground, MessageBox, _("Copying in the background.\n\nThe movie list appears updated after full completion."), MessageBox.TYPE_INFO, timeout=12)
            else:
                MovieMove(session=self.session, service=self.service)

    def DoneForeground(self, confirmed):
        self.session.current_dialog.close()
        self.session.current_dialog.csel.reloadList()

    def DoneBackground(self, confirmed):
        self.session.current_dialog.close()
            
    def skipMoveFile(self, reason):
        self.session.open(MessageBox, (_("Move/Copy aborted due to:\n%s") % reason), MessageBox.TYPE_INFO)
