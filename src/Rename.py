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
# for localized messages
from __init__ import _
from Screens.Screen import Screen
from Components.config import ConfigText, ConfigSelection, getConfigListEntry
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from enigma import eServiceReference, iServiceInformation
from ServiceProvider import ServiceCenter
import os

class MovieRetitle(Screen, ConfigListScreen):
	def __init__(self, session, service):
		Screen.__init__(self, session)
		self.skinName = [ "MovieRetitle", "Setup" ]
		self.service = service
		self.is_dir = service.flags & eServiceReference.mustDescent

		serviceHandler = ServiceCenter.getInstance()
		info = serviceHandler.info(service)
		path = service.getPath()
		if self.is_dir:
			self.original_file = service.getName()
		else:
			self.original_file = os.path.basename(os.path.splitext(path)[0]) 
		self.original_path = os.path.dirname(path)
		self.original_name = info.getName(service)
		self.original_desc = info.getInfoString(service, iServiceInformation.sDescription)

		self.input_file = ConfigText(default=self.original_file, fixed_size=False, visible_width=82)
		self.input_title = ConfigText(default=self.original_name, fixed_size=False, visible_width=82)
		self.input_descr = ConfigText(default=self.original_desc, fixed_size=False, visible_width=82)
		self.input_dir = ConfigSelection(choices=[self.original_path])

		self["key_green"] = StaticText(_("Save"))
		self["key_red"] = StaticText(_("Cancel"))

		self["actions"] = ActionMap(["SetupActions"],
		{
			"ok": self.keyGo,
			"save": self.keyGo,
			"cancel": self.keyCancel,
		}, -2)

		l = [
			getConfigListEntry(_("Filename"), self.input_file),
			getConfigListEntry(_("Title"), self.input_title),
			getConfigListEntry(_("Description"), self.input_descr),
			getConfigListEntry(_("Location"), self.input_dir)
		]
		if self.is_dir:
			del l[1:3]
		ConfigListScreen.__init__(self, l)

		self.onLayoutFinish.append(self.setCustomTitle)
		
	def setCustomTitle(self):
		self.setTitle(_("Name and Description Input"))

	def keyGo(self):
		if self.is_dir:
			if self.input_file.getText() != self.original_file:
				self.renameDirectory(self.service, self.input_file.getText())
				self.original_file = self.input_file.getText()
		else:
			if self.input_title.getText() != self.original_name or self.input_descr.getText() != self.original_desc:
				self.setTitleDescr(self.service, self.input_title.getText(), self.input_descr.getText())
				self.original_name = self.input_title.getText()
				self.original_desc = self.input_descr.getText()
			if self.input_file.getText() != self.original_file:
				self.renameFile(self.service, self.input_file.getText())
				self.original_file = self.input_file.getText()
		self.close()
	
	def keyCancel(self):
		self.close()

	def setTitleDescr(self, service, title, descr):
		if service.getPath().endswith(".ts"):
			meta_file = service.getPath() + ".meta"
		else:
			meta_file = service.getPath() + ".ts.meta"
		if os.path.exists(meta_file):
			metafile = open(meta_file, "r")
			sid = metafile.readline()
			oldtitle = metafile.readline().rstrip()
			olddescr = metafile.readline().rstrip()
			rest = metafile.read()
			metafile.close()
			if not title and title != "":
				title = oldtitle
			if not descr and descr != "":
				descr = olddescr
			metafile = open(meta_file, "w")
			metafile.write("%s%s\n%s\n%s" % (sid, title, descr, rest))
			metafile.close()

	def renameDirectory(self, service, new_name):
		try:
			print self.service.getPath()
			dir = os.path.dirname(self.service.getPath()[0:-1])
			os.rename(self.service.getPath(), os.path.join(dir, self.input_file.getText() + "/"))
			self.original_file = self.input_file.getText()
		except Exception, e:
			print e

	def renameFile(self, service, new_name):
		try:
			path = os.path.dirname(service.getPath())
			file_name = os.path.basename(os.path.splitext(service.getPath())[0])
			src = os.path.join(path, file_name)
			dst = os.path.join(path, new_name)
			import glob
			for f in glob.glob(os.path.join(path, src + "*")):
				os.rename(f, f.replace(src, dst))
		except Exception, e:
			print e
