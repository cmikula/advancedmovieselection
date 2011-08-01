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
from Components.PluginComponent import plugins
from Components.ActionMap import HelpableActionMap
from MovieSelection import MovieSelection
from MovieList import eServiceReferenceDvd
from ServiceProvider import CutListSupport
from Screens.MessageBox import MessageBox
from Screens.InfoBar import InfoBar, MoviePlayer
from Tools.Directories import fileExists, resolveFilename, SCOPE_HDD
from Components.config import config, ConfigSubsection, ConfigText, ConfigYesNo, ConfigInteger, ConfigSelection
from AdvancedMovieSelectionSetup import AdvancedMovieSelectionSetup
from enigma import ePoint 
from Rename import MovieRetitle
from TagEditor import TagEditor, MovieTagEditor

if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/IMDb/plugin.pyo"):
    IMDbPresent = True
else:
    IMDbPresent = False
if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/OFDb/plugin.pyo"):
    OFDbPresent = True
else:
    OFDbPresent = False
if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/AdvancedProgramGuide/plugin.pyo"):
    if config.plugins.AdvancedProgramGuide.Columns.value:
        from Plugins.Extensions.AdvancedProgramGuide.plugin import AdvancedProgramGuideII
    else:
        from Plugins.Extensions.AdvancedProgramGuide.plugin import AdvancedProgramGuide
    AdvancedProgramGuidePresent = True
else:
    AdvancedProgramGuidePresent = False
if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/MerlinEPG/plugin.pyo"):
    from Plugins.Extensions.MerlinEPG.plugin import Merlin_PGII, Merlin_PGd
    MerlinEPGPresent = True
else:
    MerlinEPGPresent = False
if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/CoolTVGuide/plugin.pyo"):
    CoolTVGuidePresent = True
else:
    CoolTVGuidePresent = False
if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/YTTrailer/plugin.pyo"):
    from Plugins.Extensions.YTTrailer.plugin import YTTrailerList
    YTTrailerPresent=True
else:
    YTTrailerPresent=False

config.AdvancedMovieSelection = ConfigSubsection()
config.AdvancedMovieSelection.exitprompt = ConfigYesNo(default=False)
config.AdvancedMovieSelection.exitkey = ConfigYesNo(default=False)
config.AdvancedMovieSelection.showtrailer = ConfigYesNo(default=False)
config.AdvancedMovieSelection.jump_first_mark = ConfigYesNo(default=False)
config.AdvancedMovieSelection.showfiltertags = ConfigYesNo(default=False)
config.AdvancedMovieSelection.showmovietagsinmenu = ConfigYesNo(default=False)
config.AdvancedMovieSelection.usefoldername = ConfigYesNo(default=True)
config.AdvancedMovieSelection.minitv = ConfigYesNo(default=True)
config.AdvancedMovieSelection.shownew = ConfigYesNo(default=True)
config.AdvancedMovieSelection.dateformat = ConfigSelection(default="6" , choices=[("6" , _("German (without Year)")), ("1" , _("German (with Year)")), ("3" , _("German (with Starttime)")), ("2" , _("Enigma 2 default")), ("7" , _("English (without Year)")), ("4" , _("English (with Year)")), ("5" , _("English (with Starttime)"))])
config.AdvancedMovieSelection.color1 = ConfigSelection(default="yellow" , choices=[("yellow" , _("Yellow")), ("blue" , _("Blue")), ("red" , _("Red")), ("black" , _("Black")), ("green" , _("Green"))])
config.AdvancedMovieSelection.color2 = ConfigSelection(default="green" , choices=[("green" , _("Green")), ("blue" , _("Blue")), ("red" , _("Red")), ("black" , _("Black")), ("yellow" , _("Yellow"))])
config.AdvancedMovieSelection.color3 = ConfigSelection(default="red" , choices=[("red" , _("Red")), ("blue" , _("Blue")), ("green" , _("Green")), ("black" , _("Black")), ("yellow" , _("Yellow"))])
config.AdvancedMovieSelection.moviepercentseen = ConfigInteger(default=80, limits=(50, 100))
config.AdvancedMovieSelection.showfoldersinmovielist = ConfigYesNo(default=False)
config.AdvancedMovieSelection.showprogessbarinmovielist = ConfigYesNo(default=False)
config.AdvancedMovieSelection.showiconstatusinmovielist = ConfigYesNo(default=False)
config.AdvancedMovieSelection.showcolorstatusinmovielist = ConfigYesNo(default=False)
config.AdvancedMovieSelection.about = ConfigSelection(default="1", choices=[("1", " ")])
config.AdvancedMovieSelection.ml_disable = ConfigYesNo(default=False)
config.AdvancedMovieSelection.showmenu = ConfigYesNo(default=True)
config.AdvancedMovieSelection.pluginmenu_list = ConfigYesNo(default=False)
config.AdvancedMovieSelection.red = ConfigText(default=_("Delete"), visible_width=50, fixed_size=False)
config.AdvancedMovieSelection.green = ConfigText(default=_("Nothing"), visible_width=50, fixed_size=False)
config.AdvancedMovieSelection.yellow = ConfigText(default=_("Nothing"), visible_width=50, fixed_size=False)
config.AdvancedMovieSelection.blue = ConfigText(default=_("Nothing"), visible_width=50, fixed_size=False)
config.AdvancedMovieSelection.bookmark1text = ConfigText(default=_("Bookmark 1"), visible_width=50, fixed_size=False)
config.AdvancedMovieSelection.bookmark2text = ConfigText(default=_("Bookmark 2"), visible_width=50, fixed_size=False)
config.AdvancedMovieSelection.bookmark3text = ConfigText(default=_("Bookmark 3"), visible_width=50, fixed_size=False)
config.AdvancedMovieSelection.hometext = ConfigText(default=_("Home"), visible_width=50, fixed_size=False)
config.AdvancedMovieSelection.homepath = ConfigText(default="/hdd/movie/")
config.AdvancedMovieSelection.bookmark1path = ConfigText(default="/hdd/movie/")
config.AdvancedMovieSelection.bookmark2path = ConfigText(default="/hdd/movie/")
config.AdvancedMovieSelection.bookmark3path = ConfigText(default="/hdd/movie/")
config.AdvancedMovieSelection.buttoncaption = ConfigText(default="Display plugin name")
config.AdvancedMovieSelection.homeowntext = ConfigText(default=_("Homebutton"), visible_width=50, fixed_size=False)
config.AdvancedMovieSelection.bookmark1owntext = ConfigText(default=_("Own text 1"), visible_width=50, fixed_size=False)
config.AdvancedMovieSelection.bookmark1owntext = ConfigText(default=_("Own text 2"), visible_width=50, fixed_size=False)
config.AdvancedMovieSelection.bookmark2owntext = ConfigText(default=_("Own text 3"), visible_width=50, fixed_size=False)
config.AdvancedMovieSelection.bookmark3owntext = ConfigText(default=_("Own text 4"), visible_width=50, fixed_size=False)
launch_choices = [    ("None", _("No override")),
                            ("showMovies", _("Video-button")),
                            ("showTv", _("TV-button")),
                            ("showRadio", _("Radio-button")),
                            ("timeshiftStart", _("Timeshift-button"))]
config.AdvancedMovieSelection.movie_launch = ConfigSelection(default="showMovies", choices=launch_choices)
config.AdvancedMovieSelection.askdelete = ConfigYesNo(default=True)
config.AdvancedMovieSelection.moviepercentseen = ConfigInteger(default=85, limits=(50, 100))
config.AdvancedMovieSelection.AskEventinfo = ConfigYesNo(default=True)
config.AdvancedMovieSelection.Eventinfotyp = ConfigSelection(choices=[("Ei", _("Advanced Movie Selection info")), ("Ti", _("TMDb info")), ("Ii", _("IMDb info")), ("Oi", _("OFDb info"))], default="Ei")
config.AdvancedMovieSelection.Eventinfotyp2 = ConfigSelection(choices=[("Ei", _("Advanced Movie Selection info")), ("Ii", _("IMDb info"))], default="Ei")
config.AdvancedMovieSelection.Eventinfotyp3 = ConfigSelection(choices=[("Ei", _("Advanced Movie Selection info")), ("Oi", _("OFDb info"))], default="Ei")
config.AdvancedMovieSelection.Eventinfotyp4 = ConfigSelection(choices=[("Ei", _("Advanced Movie Selection info")), ("Ti", _("TMDb info"))], default="Ei")
config.AdvancedMovieSelection.Eventinfotyp5 = ConfigSelection(choices=[("Ei", _("Advanced Movie Selection info")), ("Ti", _("TMDb info")), ("Ii", _("IMDb info"))], default="Ei")
config.AdvancedMovieSelection.Eventinfotyp6 = ConfigSelection(choices=[("Ei", _("Advanced Movie Selection info")), ("Ti", _("TMDb info")), ("Oi", _("OFDb info"))], default="Ei")
config.AdvancedMovieSelection.Eventinfotyp7 = ConfigSelection(choices=[("Ei", _("Advanced Movie Selection info")), ("Ii", _("IMDb info")), ("Oi", _("OFDb info"))], default="Ei")
config.AdvancedMovieSelection.showcolorkey = ConfigYesNo(default=True)
config.AdvancedMovieSelection.showliststyle = ConfigYesNo(default=True)
config.AdvancedMovieSelection.showextras = ConfigYesNo(default=True)
config.AdvancedMovieSelection.showsort = ConfigYesNo(default=True)
config.usage.load_length_of_movies_in_moviellist = ConfigYesNo(default=True)
config.AdvancedMovieSelection.showmark = ConfigYesNo(default=True)
config.AdvancedMovieSelection.startdir = ConfigYesNo(default=False)
config.AdvancedMovieSelection.showdelete = ConfigYesNo(default=True)
config.AdvancedMovieSelection.showmove = ConfigYesNo(default=True)
config.AdvancedMovieSelection.startonfirst = ConfigYesNo(default=True)
config.AdvancedMovieSelection.movecopydirs = ConfigText(default=resolveFilename(SCOPE_HDD))
config.AdvancedMovieSelection.showsearch = ConfigYesNo(default=True)
config.AdvancedMovieSelection.showcoveroptions = ConfigYesNo(default=True)
config.AdvancedMovieSelection.showpreview = ConfigYesNo(default=True)
config.AdvancedMovieSelection.showrename = ConfigYesNo(default=True)
config.AdvancedMovieSelection.coversize = ConfigSelection(default="cover", choices=[("original", _("Original (1000x1500)")), ("mid", _("Mid (500x750)")), ("cover", _("Cover (185x278)")), ("thumb", _("Thumb (92x138)"))])
config.AdvancedMovieSelection.description = ConfigYesNo(default=True)
config.AdvancedMovieSelection.showtmdb = ConfigYesNo(default=True)
config.AdvancedMovieSelection.show_info_cover_del = ConfigYesNo(default=True)
config.AdvancedMovieSelection.show_info_del = ConfigYesNo(default=True)
config.AdvancedMovieSelection.show_cover_del = ConfigYesNo(default=True)
config.usage.on_movie_start = ConfigSelection(default="ask", choices=[("ask", _("Ask user")), ("resume", _("Resume from last position")), ("beginning", _("Start from the beginning"))])
config.usage.on_movie_stop = ConfigSelection(default="movielist", choices=[("ask", _("Ask user")), ("movielist", _("Return to movie list")), ("quit", _("Return to previous service"))])
config.usage.on_movie_eof = ConfigSelection(default="quit", choices=[("ask", _("Ask user")), ("movielist", _("Return to movie list")), ("quit", _("Return to previous service")), ("pause", _("Pause movie at end"))])
config.AdvancedMovieSelection.movieplayer_infobar_position_offset_x = ConfigInteger(default=0)
config.AdvancedMovieSelection.movieplayer_infobar_position_offset_y = ConfigInteger(default=0)
config.AdvancedMovieSelection.show_infobar_position = ConfigYesNo(default=True)

PlayerInstance = None

class MoviePlayerExtended(CutListSupport, MoviePlayer):
    def __init__(self, session, service):
        CutListSupport.__init__(self, service)
        MoviePlayer.__init__(self, session, service)
        self.skinName = "MoviePlayer"
        self.addPlayerEvents()
        global PlayerInstance
        PlayerInstance = self
        self["EPGActions"] = HelpableActionMap(self, "InfobarEPGActions",
            {
                "showEventInfo": (self.openInfoView, _("Show event details")),
                "showEventInfoPlugin": (self.openServiceList, _("Open servicelist")),
            })
        if config.AdvancedMovieSelection.exitkey.value and config.AdvancedMovieSelection.exitprompt.value:
            self["closeactions"] = HelpableActionMap(self, "WizardActions",
                {
                    "back": (self.leavePlayer, _("Leave movie player"))
                })
        if config.AdvancedMovieSelection.exitkey.value and not config.AdvancedMovieSelection.exitprompt.value: 
            self["closeactions"] = HelpableActionMap(self, "WizardActions",
                {
                    "back": (self.close, _("Leave movie player"))
                })
        self.firstime = True
        self.onExecBegin.append(self.__onExecBegin)

    def __onExecBegin(self):
        if self.firstime:
            orgpos = self.instance.position()    
            self.instance.move(ePoint(orgpos.x() + config.AdvancedMovieSelection.movieplayer_infobar_position_offset_x.value, orgpos.y() + config.AdvancedMovieSelection.movieplayer_infobar_position_offset_y.value))
            self.firstime = False

    def openServiceList(self):
        if AdvancedProgramGuidePresent:
            if config.plugins.AdvancedProgramGuide.StartFirst.value and config.plugins.AdvancedProgramGuide.Columns.value:
                self.session.open(AdvancedProgramGuideII)
            else:
                if config.plugins.AdvancedProgramGuide.StartFirst.value and not config.plugins.AdvancedProgramGuide.Columns.value:
                    self.session.open(AdvancedProgramGuide)
                else:
                    if not config.plugins.AdvancedProgramGuide.StartFirst.value and config.plugins.AdvancedProgramGuide.Columns.value:
                        config.plugins.AdvancedProgramGuide.StartFirst.value = True
                        config.plugins.AdvancedProgramGuide.StartFirst.save()
                        self.session.openWithCallback(self.setnew, AdvancedProgramGuideII)
                    else:
                        if not config.plugins.AdvancedProgramGuide.StartFirst.value and not config.plugins.AdvancedProgramGuide.Columns.value:
                            config.plugins.AdvancedProgramGuide.StartFirst.value = True
                            config.plugins.AdvancedProgramGuide.StartFirst.save()
                            self.session.openWithCallback(self.setnew, AdvancedProgramGuide)
        else:
            if MerlinEPGPresent and not AdvancedProgramGuidePresent and not CoolTVGuidePresent:
                if config.plugins.MerlinEPG.StartFirst.value and config.plugins.MerlinEPG.Columns.value:
                    self.session.open(Merlin_PGII)
                else:
                    if config.plugins.MerlinEPG.StartFirst.value and not config.plugins.MerlinEPG.Columns.value:
                        self.session.open(Merlin_PGd)
                    else:
                        if not config.plugins.MerlinEPG.StartFirst.value and config.plugins.MerlinEPG.Columns.value:
                            config.plugins.MerlinEPG.StartFirst.value = True
                            config.plugins.MerlinEPG.StartFirst.save()
                            self.session.openWithCallback(self.setnew2, Merlin_PGII)
                        else:
                            if not config.plugins.MerlinEPG.StartFirst.value and not config.plugins.MerlinEPG.Columns.value:
                                config.plugins.MerlinEPG.StartFirst.value = True
                                config.plugins.MerlinEPG.StartFirst.save()
                                self.session.openWithCallback(self.setnew2, Merlin_PGd)
            else:
                if CoolTVGuidePresent and not AdvancedProgramGuidePresent and not MerlinEPGPresent:
                    from Plugins.Extensions.CoolTVGuide.plugin import main as ctvmain
                    ctvmain(self.session)
                else:
                    self.session.open(MessageBox, _("Not possible !\nMerlinEPG and CoolTVGuide present or neither installed from this two plugins."), MessageBox.TYPE_INFO)
            
    def setnew(self):
        config.plugins.AdvancedProgramGuide.StartFirst.value = False
        config.plugins.AdvancedProgramGuide.StartFirst.save()

    def setnew2(self):
        config.plugins.MerlinEPG.StartFirst.value = False
        config.plugins.MerlinEPG.StartFirst.save()
            
    def openInfoView(self):
        from AdvancedMovieSelectionEventView import EventViewSimple
        serviceref = self.session.nav.getCurrentlyPlayingServiceReference()
        from ServiceProvider import ServiceCenter
        info = ServiceCenter.getInstance().info(serviceref)
        evt = info.getEvent(serviceref)
        if evt:
            self.session.open(EventViewSimple, evt, serviceref)

    def showMovies(self):
        ref = self.session.nav.getCurrentlyPlayingServiceReference()
        self.session.openWithCallback(self.movieSelected, MovieSelection, ref)

    def leavePlayerConfirmed(self, answer):
        answer = answer and answer[1]
        if answer in ("quitanddelete", "quitanddeleteconfirmed"):
            ref = self.session.nav.getCurrentlyPlayingServiceReference()
            from enigma import eServiceCenter
            serviceHandler = eServiceCenter.getInstance()
            info = serviceHandler.info(ref)
            name = info and info.getName(ref) or _("this recording")

            if answer == "quitanddelete":
                self.session.openWithCallback(self.deleteConfirmed, MessageBox, _("Do you really want to delete %s?") % name)
                return
            elif answer == "quitanddeleteconfirmed":
                offline = serviceHandler.offlineOperations(ref)
                if offline.deleteFromDisk(0):
                    self.session.openWithCallback(self.close, MessageBox, _("You cannot delete this!"), MessageBox.TYPE_ERROR)
                    return
        if answer in ("quit", "quitanddeleteconfirmed"):
            self.close()
        elif answer == "movielist":
            self.playerClosed()
            ref = self.session.nav.getCurrentlyPlayingServiceReference()
            self.returning = True
            self.session.openWithCallback(self.movieSelected, MovieSelection, ref, True)
            self.session.nav.stopService()
            self.session.nav.playService(self.lastservice)
        elif answer == "restart":
            self.doSeek(0)
            self.setSeekState(self.SEEK_STATE_PLAY)

def showMovies(self):
    global PlayerInstance
    PlayerInstance = None
    if config.AdvancedMovieSelection.startonfirst.value:
        self.session.openWithCallback(self.movieSelected, MovieSelection)
    else:
        self.session.openWithCallback(self.movieSelected, MovieSelection, self.session.currentSelection)

def movieSelected(self, service):
    if service is not None:
        if isinstance(service, eServiceReferenceDvd):
            if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/DVDPlayer/plugin.py"):
                from Plugins.Extensions.DVDPlayer.plugin import DVDPlayer
                class DVDPlayerExtended(CutListSupport, DVDPlayer):
                    def __init__(self, session, service):
                        CutListSupport.__init__(self, service)
                        DVDPlayer.__init__(self, session, dvd_filelist=service.getDVD())
                        self.addPlayerEvents()
                        self.skinName = "DVDPlayer"
                try:
                    global PlayerInstance
                    if PlayerInstance is not None:
                        PlayerInstance.playerClosed()
                        self.session.nav.stopService()
                        PlayerInstance.close()
                        PlayerInstance = None
                except Exception, e:
                    print "Player instance closed exception: " + str(e) 

                self.session.open(DVDPlayerExtended, service)
            else:
                self.session.open(MessageBox, _("No DVD-Player found!"), MessageBox.TYPE_ERROR, 10)
        else:
            self.session.open(MoviePlayerExtended, service)

def autostart(reason, **kwargs):
    if reason == 0:
        session = kwargs["session"]
        session.currentSelection = None
        if not config.AdvancedMovieSelection.ml_disable.value:
            try:
                InfoBar.movieSelected = movieSelected
                value = config.AdvancedMovieSelection.movie_launch.value
                if value == "showMovies": InfoBar.showMovies = showMovies
                elif value == "showTv": InfoBar.showTv = showMovies
                elif value == "showRadio": InfoBar.showRadio = showMovies
                elif value == "timeshiftStart": InfoBar.startTimeshift = showMovies
            except:
                pass

def tageditor(session, service, **kwargs):
    session.open(MovieTagEditor, service, session.current_dialog, **kwargs)

def rename(session, service, **kwargs):
    session.open(MovieRetitle, service, session.current_dialog, **kwargs)

def pluginOpen(session, **kwargs):
    session.open(AdvancedMovieSelectionSetup)

def Setup(menuid, **kwargs):
    if menuid == "setup":
        return [(_("Setup Advanced Movie Selection"), pluginOpen, "SetupAdvancedMovieSelection", None)]
    return []

def nostart(reason, **kwargs):
    print"[Advanced Movie Selection] -----> disabled"
    pass

def Plugins(**kwargs):
    try:
        from MovieSelection import setPreferredTagEditor
        setPreferredTagEditor(TagEditor)
    except Exception, e:
        print e
    if not config.AdvancedMovieSelection.ml_disable.value:
        descriptors = [PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=autostart)]
        descriptors.append(PluginDescriptor(name="Movie Retitle", description=_("Rename"), where=PluginDescriptor.WHERE_MOVIELIST, fnc=rename))
        descriptors.append(PluginDescriptor(name="Tag Editor", description=_("Tag Editor"), where=PluginDescriptor.WHERE_MOVIELIST, fnc=tageditor))
        descriptors.append(PluginDescriptor(where=PluginDescriptor.WHERE_MENU, fnc=Setup))
    else:
        descriptors = [PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=nostart)]
        descriptors.append(PluginDescriptor(where=PluginDescriptor.WHERE_MENU, fnc=Setup))
    return descriptors
