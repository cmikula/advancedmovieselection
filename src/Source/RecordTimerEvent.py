#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Copyright (C) 2012 cmikula

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
from Globals import printStackTrace
from EITTools import eitFromTMDb, downloadTMDbSerie, downloadTMDbEpisode, createEITtvdb

class RecordTimerEvent():
    def __init__(self):
        self.on_state_changed = []
        import NavigationInstance
        if not self.timerStateChanged in NavigationInstance.instance.RecordTimer.on_state_change:
            NavigationInstance.instance.RecordTimer.on_state_change.append(self.timerStateChanged)

    def appendCallback(self, callback):
        if not callback in self.on_state_changed:
            self.on_state_changed.append(callback)

    def removeCallback(self, callback):
        if callback in self.on_state_changed:
            self.on_state_changed.remove(callback)

    def timerStateChanged(self, timer):
        try:
            print "[AdvancedMovieSelection] timer state changed event"
            print str(timer.justplay), str(timer.cancelled), str(timer.state) 
            if timer.justplay:
                print "[AdvancedMovieSelection] cancel justplay event"
                return
            if not hasattr(timer, 'Filename'):
                print "[AdvancedMovieSelection] cancel timer state changed, no Filename in timer event"
                return
            for callback in self.on_state_changed:
                callback(timer)
        except:
            printStackTrace()

recordTimerEvent = RecordTimerEvent()

from Components.config import config

class CoverLoader():
    def __init__(self):
        recordTimerEvent.appendCallback(self.timerStateChanged)

    def getTimerEntryDownloadType(self, timer):
        try:
            if hasattr(timer, 'plugins'):
                ams_timer = timer.plugins.get("AMS_COVER_DOWNLOAD")
                print "timer.plugins", str(ams_timer)
                if ams_timer is not None:
                    download = ams_timer[0];
                    print download
                    return download
            
            print "no timer.plugins!!!"
            default = config.AdvancedMovieSelection.timer_download_type.value
            if default:
                print "timer_download_type:", str(default)
            return default
        except:
            printStackTrace()
    
    def timerStateChanged(self, timer):
        if not config.AdvancedMovieSelection.cover_auto_download.value:
            return
        from timer import TimerEntry
        print "[AdvancedMovieSelection] RecordTimerEvent:", str(timer.state), str(timer.cancelled), str(timer.begin), str(timer.end), timer.Filename
        duration_minutes = (timer.end - timer.begin) / 60
        print duration_minutes
        # if timer.state == TimerEntry.StateRunning and duration_minutes > 80:
        if timer.state == TimerEntry.StateEnded: # and duration_minutes > 80:
            download_type = self.getTimerEntryDownloadType(timer)
            if download_type:
                print "[AdvancedMovieSelection] RecordTimerEvent, loading info"
                print "Name:", timer.name
                print "Description:", timer.description
                print "Download:", download_type
                from thread import start_new_thread
                start_new_thread(self.downloadMovieInfo, (download_type, timer.name, timer.description, timer.Filename))

    def downloadMovieInfo(self, download_type, name, description, filename):
        try:
            if not filename.endswith(".ts"):
                filename += ".ts"
            if download_type == "tmdb_movie":
                eitFromTMDb(filename, name)
            if download_type == "tmdb_serie":
                #downloadTMDbSerie(filename, name)
                downloadTMDbEpisode(filename, name, description)
            if download_type == "tvdb_serie":
                createEITtvdb(filename, name)
        except:
            printStackTrace()


coverLoader = CoverLoader()
