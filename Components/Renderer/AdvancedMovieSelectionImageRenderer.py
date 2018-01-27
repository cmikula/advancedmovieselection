#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  Coded by cmikula (c)2018
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
import os
from Components.AVSwitch import AVSwitch
from Components.Sources.CurrentService import CurrentService
from Tools.Directories import fileExists, resolveFilename, SCOPE_CURRENT_PLUGIN, SCOPE_CURRENT_SKIN, SCOPE_SKIN_IMAGE
from Components.Renderer.Renderer import Renderer
from Components.Renderer.Pixmap import Pixmap
from enigma import ePixmap, gPixmapPtr, eServiceReference
from Plugins.Extensions.AdvancedMovieSelection.Source.Globals import getNocover
from Plugins.Extensions.AdvancedMovieSelection.Source.PicLoader import PicLoader
'''
		<!--Renderer test -->
        <widget position="20,20" size="200,200" type="cover" render="AdvancedMovieSelectionImageRenderer" source="session.AdvancedMovieSelection" default="plugin"/>

usage:
movieplayer:
	<widget position="20,20" size="200,200" type="backdrop" render="AdvancedMovieSelectionImageRenderer" source="ServiceEvent"/>
movielist current selected movie in list:
	<widget position="20,20" size="200,200" type="cover" render="AdvancedMovieSelectionImageRenderer" source="session.AdvancedMovieSelection"/>
global current playing service:
	<widget position="20,20" size="200,200" type="cover" render="AdvancedMovieSelectionImageRenderer" source="session.CurrentService"/>
'''

class AdvancedMovieSelectionImageRenderer(Renderer):
	GUI_WIDGET = ePixmap
	def __init__(self):
		Renderer.__init__(self)
		self.picload = PicLoader()
		self.picload.addCallback(self.__loadImage)
		self.extension = ".jpg"
		self.default_image = None

	def destroy(self):
		self.picload.destroy()
		Renderer.destroy(self)

	def imageFileFromService(self, serviceref):
		if not isinstance(serviceref, eServiceReference):
			return None
		path = serviceref.getPath()
		if serviceref.flags & eServiceReference.mustDescent:
			# directory
			if fileExists(path + self.extension):
				path += self.extension
			#elif config.AdvancedMovieSelection.usefoldername.value:
			#	path = path[:-1] + ".jpg"
			#else:
			#	path = path + "folder.jpg"
		elif os.path.isfile(path):
			# file service
			path_s = os.path.splitext(path)[0]
			path = path_s + self.extension
		else:   
			# structure service
			path = path + self.extension
		return os.path.isfile(path) and path or None

	def __loadImage(self, picInfo=None):
		if picInfo:
			ptr = self.picload.getData()
			if ptr is not None and self.working:
				self.instance.setPixmap(ptr)
			else:
				self.instance.setPixmap(gPixmapPtr())
		self.working = False

#	def postWidgetCreate(self, instance):
#		self.changed((self.CHANGED_DEFAULT,))

	def applySkin(self, desktop, parent):
		attribs = self.skinAttributes[:]
		for (attrib, value) in self.skinAttributes:
			if attrib == "size":
				size = value.split(',')
				sc = AVSwitch().getFramebufferScale()
				self.picload.setPara((int(size[0]), int(size[1]), sc[0], sc[1], False, 1, "#ff000000"))
			if attrib == "type":
				#if value == "cover":
				#	pass
				if value == "backdrop":
					self.extension = ".backdrop.jpg"
				attribs.remove((attrib, value))
			if attrib == "default":
				image = resolveFilename(SCOPE_CURRENT_SKIN) + value
				if fileExists(image):
					self.default_image = image
				image = resolveFilename(SCOPE_SKIN_IMAGE) + value
				if fileExists(image):
					self.default_image = image
				if self.default_image is None:
					self.default_image = getNocover()
				attribs.remove((attrib, value))

		# session.CurrentService
		if isinstance(self.source, CurrentService):
			self.changed((self.CHANGED_DEFAULT,))
				
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	def getServiceRef(self):
		if isinstance(self.source, CurrentService):
			return  self.source.navcore.getCurrentlyPlayingServiceReference()
		else:
			return self.source.service
	
	def changed(self, what):
		if self.instance is not None:
			if what[0] != self.CHANGED_CLEAR:
				service = self.getServiceRef()
				cover_path = self.imageFileFromService(service)
				if cover_path is None:
					cover_path = self.default_image
				if cover_path is not None:
					self.working = True
					self.picload.startDecode(cover_path)
					return
			self.instance.setPixmap(gPixmapPtr())

		