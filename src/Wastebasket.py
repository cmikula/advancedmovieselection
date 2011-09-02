#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Copyright (C) 2011 cmikula

Trash can gui for Advanced Movie Selection

In case of reuse of this source code please do not remove this copyright.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

For more information on the GNU General Public License see:
<http://www.gnu.org/licenses/>.

For example, if you distribute copies of such a program, whether gratis or for a fee, you 
must pass on to the recipients the same freedoms that you received. You must make sure 
that they, too, receive or can get the source code. And you must show them these terms so they know their rights.
'''

from __init__ import _
from MovieSelection import MovieSelection
from MovieList import MovieList
from Trashcan import Trashcan
from Components.config import config
from Components.ActionMap import HelpableActionMap
from Components.Button import Button
from Components.Label import Label
from ServiceProvider import ServiceCenter
from Screens.MessageBox import MessageBox

class TrashList(MovieList):
    def load(self, root, filter_tags):
        self.list = [ ]
        self.serviceHandler = ServiceCenter.getInstance()
        if config.AdvancedMovieSelection.wastelist_buildtype.value == 'listMovies':
            trash = Trashcan.listMovies(root.getPath())
        if config.AdvancedMovieSelection.wastelist_buildtype.value == 'listAllMovies':
            trash = Trashcan.listAllMovies(root.getPath())
        if config.AdvancedMovieSelection.wastelist_buildtype.value == 'listAllMoviesMedia':
            trash = Trashcan.listAllMovies("/media")
        for service in trash:
            print service.getPath()
            info = self.serviceHandler.info(service)
            self.list.append((service, info, -1, -1))

class Wastebasket(MovieSelection):
    def __init__(self, session):
        MovieSelection.__init__(self, session)
        self["key_red"] = Button(_("Delete permanent"))
        self["key_green"] = Button(_("Restore movie"))
        self["key_yellow"] = Button(_("Delete all"))
        self["key_blue"] = Button()
        self["waitingtext"] = Label(_("Please wait... Loading trash list..."))
        self["ColorActions"] = HelpableActionMap(self, "ColorActions",
        {
            "red": (self.canDelete, _("Delete movie permanent")),
            "green": (self.restore, _("Restore movie")),
            "yellow": (self.canDeleteAll, _("Delete all movies")),
        })

        self["list"] = TrashList(None,
            config.movielist.listtype.value,
            config.movielist.moviesort.value,
            config.movielist.description.value,
            config.AdvancedMovieSelection.showfoldersinmovielist.value,
            config.AdvancedMovieSelection.showprogessbarinmovielist.value,
            config.AdvancedMovieSelection.showiconstatusinmovielist.value,
            config.AdvancedMovieSelection.showcolorstatusinmovielist.value,
            config.movielist.showdate.value,
            config.movielist.showtime.value,
            config.movielist.showservice.value,
            config.movielist.showtags.value)
        self.list = self["list"]
        self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
            {
                "cancel": (self.abort, _("Exit movielist"))
            })

    def canDelete(self):
        self.service = self.getCurrent()
        if not self.service:
            return
        if config.AdvancedMovieSelection.askdelete.value:
            self.session.openWithCallback(self.delete, MessageBox, _("Do you really want to delete %s?") % (self.service.getName()))
        else:
            self.delete(True)

    def canDeleteAll(self):
        self.service = self.getCurrent()
        if not self.service:
            return
        if config.AdvancedMovieSelection.askdelete.value:
            self.session.openWithCallback(self.deleteAll, MessageBox, _("Do you really want to delete all movies?"))
        else:
            self.deleteAll(True)

    def delete(self, confirmed):
        if not confirmed:
            return
        try:
            Trashcan.delete(self.service.getPath())
        except Exception, e:
            print e
            self.session.open(MessageBox, _("Delete failed!"), MessageBox.TYPE_ERROR)
            return
        
        self["list"].removeService(self.service)

    def deleteAll(self, confirmed):
        if not confirmed:
            return
        deleted = []
        try:
            for x in self.list.list:
                service = x[0]
                Trashcan.delete(service.getPath())
                deleted.append(service)
        except Exception, e:
            print e
            self.session.open(MessageBox, _("Delete failed!"), MessageBox.TYPE_ERROR)
        for service in deleted:
            self["list"].removeService(service)
        
    def restore(self):
        try:
            if not self.getCurrent():
                return
            Trashcan.restore(self.getCurrent().getPath())
        except Exception, e:
            print e
            self.session.open(MessageBox, _("Restore failed!"), MessageBox.TYPE_ERROR)
            return
        
        self["list"].removeService(self.getCurrent())
