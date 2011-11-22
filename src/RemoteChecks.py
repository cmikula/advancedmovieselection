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
#from __init__ import _
from Components.config import config
from twisted.internet import reactor
from twisted.web import client
from twisted.web.client import HTTPClientFactory
from base64 import encodestring
import xml.etree.cElementTree

class myHTTPClientFactory(HTTPClientFactory):
	def __init__(self, url, method='GET', postdata=None, headers=None,
	agent="Twisted Remotetimer", timeout=0, cookies=None,
	followRedirect=1, lastModified=None, etag=None):
		HTTPClientFactory.__init__(self, url, method=method, postdata=postdata,
		headers=headers, agent=agent, timeout=timeout, cookies=cookies,followRedirect=followRedirect)

def sendRemoteBoxWebCommand(url, contextFactory=None, timeout=60, username = "root", password = "", *args, **kwargs):
	scheme, host, port, path = client._parse(url)
	basicAuth = encodestring(("%s:%s") % (username, password))
	authHeader = "Basic " + basicAuth.strip()
	AuthHeaders = {"Authorization": authHeader}
	if kwargs.has_key("headers"):
		kwargs["headers"].update(AuthHeaders)
	else:
		kwargs["headers"] = AuthHeaders
	factory = myHTTPClientFactory(url, *args, **kwargs)
	reactor.connectTCP(host, port, factory, timeout=timeout)
	return factory.deferred

class RemoteStandbyCheck():
    def __init__(self):
        self.list = [ ]
        for c in config.AdvancedMovieSelection.Entries:
            res = [c]
            self.ip = "%d.%d.%d.%d" % tuple(c.ip.value)
            self.port = "%d" % (c.port.value)
            self.password = "%s" % (c.password.value)
            self.username = "root"
            self.http = "http://%s:%s" % (self.ip, self.port)
        
        url = self.http + "/web/powerstate"
        sendRemoteBoxWebCommand(url, None,10, self.username, self.password).addCallback(self.FillStandbyList).addErrback(self.Error)

    def FillStandbyList(self, xmlstring):
        Standby = []
        try: root = xml.etree.cElementTree.fromstring(xmlstring)
        except: Standby 
        print "1" * 50, root
        for state in root.findall("e2powerstate"):
            powerstate = 0
            try: powerstate = str(state.findtext("e2instandby", 0))
            except: powerstate = 0
            print "2" * 50, powerstate
            # achtung baustelle

    def Error(self, error = None):
        if error is not None:
            err = str(error.getErrorMessage())
            print "[AdvancedMovieSelection] Error by remote standby check: ->", err

class RemoteTimerCheck():
    def __init__(self):
        for c in config.AdvancedMovieSelection.Entries:
            res = [c]
            self.ip = "%d.%d.%d.%d" % tuple(c.ip.value)
            self.port = "%d" % (c.port.value)
            self.password = "%s" % (c.password.value)
            self.username = "root"
            self.http = "http://%s:%s" % (self.ip, self.port)
        
        url = self.http + "/web/timerlist"
        sendRemoteBoxWebCommand(url, None,10, self.username, self.password).addCallback(self.FillTimerList).addErrback(self.Error)

    def FillTimerList(self, xmlstring):
        TimerList = []
        try: root = xml.etree.cElementTree.fromstring(xmlstring)
        except: TimerList 
        for rec in root.findall("e2timer"):
            state = 0
            try: state = int(rec.findtext("e2state", 0))
            except: state = 0
            TimerList.append(state)
        return TimerList

    def Error(self, error = None):
        if error is not None:
            err = str(error.getErrorMessage())
            print "[AdvancedMovieSelection] Error by remote timer check: ->", err
    