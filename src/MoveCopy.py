#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  The plugin is developed on the basis from a lot of single plugins (thx for the code @ all)
#  Coded by JackDaniel & cmikula (c)2011
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
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.LocationBox import MovieLocationBox
from Components.config import config
from ServiceUtils import serviceUtil, realSize
from ServiceProvider import ServiceCenter
import time

def showFinished(job, session):
    from MovieSelection import MovieSelection
    if isinstance(session.current_dialog, MovieSelection):
        session.current_dialog.updateList(job)
        return
    error = job.getError()
    if session and (not isinstance(session.current_dialog, MoveCopyProgress) or error):
        movie_count = job.getMovieCount()
        full = job.getSizeTotal()
        copied = job.getSizeCopied()
        elapsed_time = job.getElapsedTime()
        b_per_sec = copied / (elapsed_time)
        message_type = MessageBox.TYPE_INFO
        mode = job.getMode() and _("moved") or _("copied")
        if job.isCanceled():
            mode = _("canceled")
        if error:
            message_type = MessageBox.TYPE_ERROR
            mode = _("Error")
        etime = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        text = _("Job finished") + "\r\n\r\n"
        if error:
            text += mode + ": " + str(error) + "\r\n"
        else:
            text += "* %s\r\n" % (job.getDestinationPath())
            text += "* %d %s %s %s\r\n" % (movie_count, _("movie(s)"), realSize(full), mode)
            text += "* %s %s\r\n" % (_("Duration"), etime)
            text += "* %s %s/S\r\n" % (_("Average"), realSize(b_per_sec, 3))
        session.open(MessageBox, text, message_type)

from Components.GUIComponent import GUIComponent
from enigma import eListboxPythonMultiContent, eListbox, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT
from Components.MultiContent import MultiContentEntryText, MultiContentEntryProgress

class ProgressList(GUIComponent):
    def __init__(self):
        GUIComponent.__init__(self)
        self.list = []
        self.l = eListboxPythonMultiContent()
        self.l.setFont(0, gFont("Regular", 20))
        self.l.setFont(1, gFont("Regular", 18))
        self.l.setFont(2, gFont("Regular", 16))
        self.l.setItemHeight(75)
        self.l.setBuildFunc(self.buildListEntry)
        
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

    def buildListEntry(self, job):
        res = [ None ]
        width = self.l.getItemSize().width()

        full = job.getSizeTotal()
        copied = job.getSizeCopied()
        elapsed_time = job.getElapsedTime()
        progress = copied * 100 / full
        b_per_sec = copied / (elapsed_time)
        mode = job.getMode() and _("Move") or _("Copy")
        if job.isCanceled():
            mode = _("Canceled")
        if job.isFinished():
            mode = _("Finished")
            movie_name = job.getDestinationPath()
        else:
            movie_name = job.getMovieName()
        error = job.getError() 
        if error:
            movie_name = str(error)
            mode = _("Error")
        etime = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        main_info = "%s (%d/%d) %s %d%%" % (mode, job.getMovieIndex(), job.getMovieCount(), realSize(full), progress)
        file_info = "(%d/%d)" % (job.getFileIndex(), job.getFileCount())
        speed_info = _("Total files") + file_info + " " + _("Average") + " " + realSize(b_per_sec, 3) + "/" + _("Seconds")
        res.append(MultiContentEntryProgress(pos=(5, 3), size=(width-10, 5), percent=progress, borderWidth=1))
        res.append(MultiContentEntryText(pos=(5, 10), size=(width - 150, 26), font=0, flags=RT_HALIGN_LEFT, text=main_info))
        res.append(MultiContentEntryText(pos=(width - 150, 10), size=(150, 26), font=0, flags=RT_HALIGN_RIGHT, text=realSize(copied)))
        res.append(MultiContentEntryText(pos=(5, 32), size=(width - 150, 22), font=1, flags=RT_HALIGN_LEFT, text=movie_name))
        res.append(MultiContentEntryText(pos=(width - 150, 32), size=(150, 22), font=1, flags=RT_HALIGN_RIGHT, text=etime))
        res.append(MultiContentEntryText(pos=(5, 54), size=(width - 205, 20), font=2, flags=RT_HALIGN_LEFT, text=speed_info))
        return res

    def moveToIndex(self, index):
        self.instance.moveSelectionTo(index)

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()

    def getCurrentEvent(self):
        l = self.l.getCurrentSelection()
        return l and l[0] and l[1] and l[1].getEvent(l[0])

    def getCurrent(self):
        l = self.l.getCurrentSelection()
        return l and l[0]

    GUI_WIDGET = eListbox

    def postWidgetCreate(self, instance):
        instance.setContent(self.l)
        instance.selectionChanged.get().append(self.selectionChanged)

    def preWidgetRemove(self, instance):
        instance.setContent(None)
        instance.selectionChanged.get().remove(self.selectionChanged)

    def load(self, jobs):
        self.list = []
        for job in jobs:
            self.list.append((job,))
        self.l.setList(self.list)

    def updateJobs(self):
        for index, job in enumerate(self.list):
            self.l.invalidateEntry(index)

    def __len__(self):
        return len(self.list)

    def moveTo(self, serviceref):
        count = 0
        for x in self.list:
            if x[0] == serviceref:
                self.instance.moveSelectionTo(count)
                return True
            count += 1
        return False
    
    def moveDown(self):
        self.instance.moveSelection(self.instance.moveDown)

from Screens.Screen import Screen
from enigma import eTimer
from Components.ActionMap import HelpableActionMap
from Components.Button import Button

class MoveCopyProgress(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.timer = eTimer()
        self.timer.callback.append(self.update)
        self["ColorActions"] = HelpableActionMap(self, "ColorActions",
        {
            "red": (self.abort, _("Abort selected job")),
            "green": (self.close, _("Close")),
        })
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Close"))
        self["list"] = ProgressList()
        self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
            {
                "cancel": (self.close, _("Close"))
            })
        self.onShown.append(self.setWindowTitle)
    
    def setWindowTitle(self):
        self.setTitle(_("Move/Copy progress"))
        self["list"].load(serviceUtil.getJobs())
        self.timer.start(500, False)
        
    def cancel(self):
        self.close()
    
    def abort(self):
        job = self["list"].getCurrent()
        if not job or job and job.isFinished():
            return
        if job and job.isCanceled():
            text = _("Job already canceled!") + "\r\n"
            text += _("Please wait until current movie is copied to the end!")
            self.session.openWithCallback(self.abortCallback, MessageBox, text, MessageBox.TYPE_INFO)
            return
        text = _("Would you really abort current job?") + "\r\n"
        text += _("Movies began to be copied until they are finished")
        self.session.openWithCallback(self.abortCallback, MessageBox, text, MessageBox.TYPE_YESNO)
    
    def abortCallback(self, result):
        if result == True:
            job = self["list"].getCurrent()
            if job:
                job.cancel()
    
    def update(self):
        self["list"].updateJobs()

class MovieMove(ChoiceBox):
    def __init__(self, session, csel, service):
        self.csel = csel
        serviceHandler = ServiceCenter.getInstance()
        info = serviceHandler.info(service)
        self.sourcepath = service.getPath().rsplit('/', 1)[0]
        if len(self.csel.list.multiSelection) == 0:
            self.name = info.getName(service)
            self.service_list = [service]
        else:
            self.name = _("Selected movies")
            self.service_list = self.csel.list.multiSelection  
        
        for s in self.service_list:
            info = serviceHandler.info(s)
            name = info.getName(s)
            s.setName(name)

        cbkeys = []
        listpath = []
        listpath.append((_("To adjusted move/copy location"), "CALLFUNC", self.selectedLocation))
        cbkeys.append("blue")
        listpath.append((_("Directory Selection"), "CALLFUNC", self.selectDir))
        cbkeys.append("yellow")
        listpath.append((_("Show active move/copy processes"), "CALLFUNC", self.showActive))
        cbkeys.append("green")
        listpath.append((_("Close"), "CALLFUNC", self.close))
        cbkeys.append("red")

        ChoiceBox.__init__(self, session, list=listpath, keys=cbkeys)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_("Move/Copy from: %s") % self.name)

    def selectedLocation(self, arg):
        self.checkLocation(config.AdvancedMovieSelection.movecopydirs.value)

    def selectDir(self, arg):
        self.session.openWithCallback(self.checkLocation, MovieLocationBox, (_("Move/Copy %s") % self.name) + ' ' + _("to:"), config.movielist.last_videodir.value)

    def showActive(self, arg):
        self.session.open(MoveCopyProgress)

    def checkLocation(self, destinationpath):
        if self.csel.getCurrentPath() == destinationpath:
            self.session.open(MessageBox, _("Source and destination path must be different."), MessageBox.TYPE_INFO)
            return
        if destinationpath:
            self.gotFilename(destinationpath)

    def gotFilename(self, destinationpath):
        if destinationpath:
            self.destinationpath = destinationpath
            listtmp = [(_("Move"), "move"), (_("Copy"), "copy"), (_("Abort"), "abort") ]
            self.session.openWithCallback(self.doAction, ChoiceBox, title=((_("How to proceed '%s'") % self.name) + ' ' + (_("from %s") % self.sourcepath) + ' ' + (_("to %s") % self.destinationpath) + ' ' + _("be moved/copied?")), list=listtmp)
    
    def doAction(self, confirmed):
        if not confirmed or confirmed[1] == "abort":
            return
        action = confirmed[1]
        serviceUtil.setCallback(showFinished, self.session)
        serviceUtil.setServices(self.service_list, self.destinationpath)
        services = serviceUtil.prepare()
        if len(services) != 0:
            serviceUtil.clear()
            text = []
            for s in services:
                print s.getName()
                text.append(s.getName())
            self.session.open(MessageBox, _("Service(s) are available in destination directory. Operation canceled!") + "\r\n\r\n" + "\r\n".join(text), MessageBox.TYPE_INFO)
            return
        if action == "copy":
            serviceUtil.copy()
        elif action == "move":
            serviceUtil.move()
        self.session.openWithCallback(self.__doClose, MoveCopyProgress)

    def __doClose(self, dummy=None):
        self.csel.reloadList()
        self.close()
