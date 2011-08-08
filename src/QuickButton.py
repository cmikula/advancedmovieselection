from __init__ import _
from Components.config import config
from Components.ActionMap import HelpableActionMap
from Components.Button import Button
from MovieList import MovieList
from Components.PluginComponent import plugins
from Plugins.Plugin import PluginDescriptor
from MoveCopy import MovieMove
from Screens.MessageBox import MessageBox
from Rename import MovieRetitle

def getPluginCaption(pname):
    if pname != _("Nothing"):
        if pname == _("Delete"):
            return _("Delete")
        elif pname == _("Home"):
            return _(config.AdvancedMovieSelection.hometext.value)
        elif pname == _("Bookmark 1"):
            return _(config.AdvancedMovieSelection.bookmark1text.value)
        elif pname == _("Bookmark 2"):
            return _(config.AdvancedMovieSelection.bookmark2text.value)
        elif pname == _("Bookmark 3"):
            return _(config.AdvancedMovieSelection.bookmark3text.value)
        elif pname == _("Sort"):
            if config.movielist.moviesort.value == MovieList.SORT_ALPHANUMERIC:
                return _("Sort by Date (1->9)")
            else:
                if config.movielist.moviesort.value == MovieList.SORT_DATE_DESC:
                    return _("Sort by Date (9->1)")
                else:
                    if config.movielist.moviesort.value == MovieList.SORT_DATE_ASC:
                        return _("Sort alphabetically")
        elif pname == _("Filter by Tags"):
            return _("Filter by Tags")
        elif pname == _("Trailer search"):
            return _("Trailer search")
        elif pname == _("Move-Copy"):
            return _("Move-Copy")
        elif pname == _("Rename"):
            return _("Rename") 
        else:
            for p in plugins.getPlugins(where=[PluginDescriptor.WHERE_MOVIELIST]):
                if pname == str(p.name):
                    if config.AdvancedMovieSelection.buttoncaption.value == "1":
                        return p.description
                    else:
                        return p.name
    return ""


class QuickButton:
    def __init__(self):
        self["key_red"] = Button(getPluginCaption(str(config.AdvancedMovieSelection.red.value)))
        self["key_green"] = Button(getPluginCaption(str(config.AdvancedMovieSelection.green.value)))
        self["key_yellow"] = Button(getPluginCaption(str(config.AdvancedMovieSelection.yellow.value)))
        self["key_blue"] = Button(getPluginCaption(str(config.AdvancedMovieSelection.blue.value)))
        self["ColorActions"] = HelpableActionMap(self, "ColorActions",
        {
            "red": (self.redpressed, _("Assigned function for red key")),
            "green": (self.greenpressed, _("Assigned function for green key")),
            "yellow": (self.yellowpressed, _("Assigned function for yellow key")),
            "blue": (self.bluepressed, _("Assigned function for blue key")),
        })

    def redpressed(self):
        self.startPlugin(str(config.AdvancedMovieSelection.red.value), 0)
    
    def greenpressed(self):
        self.startPlugin(str(config.AdvancedMovieSelection.green.value), 1)
    
    def yellowpressed(self):
        self.startPlugin(str(config.AdvancedMovieSelection.yellow.value), 2)
    
    def bluepressed(self):
        self.startPlugin(str(config.AdvancedMovieSelection.blue.value), 3)
    
    def startPlugin(self, pname, index):
        home = config.AdvancedMovieSelection.homepath.value
        bookmark1 = config.AdvancedMovieSelection.bookmark1path.value
        bookmark2 = config.AdvancedMovieSelection.bookmark2path.value
        bookmark3 = config.AdvancedMovieSelection.bookmark3path.value
        plugin = None
        no_plugin = True
        msgText = _("Unknown Error")
        current = self.getCurrent()
        service = self.getCurrent()
        if current is not None:
            if pname != _("Nothing"):
                if pname == _("Delete"):
                    self.delete()
                    no_plugin = False
                elif pname == _("Home"):
                    self.gotFilename(home)
                    no_plugin = False
                elif pname == _("Bookmark 1"):
                    self.gotFilename(bookmark1)
                    no_plugin = False
                elif pname == _("Bookmark 2"):
                    self.gotFilename(bookmark2)
                    no_plugin = False
                elif pname == _("Bookmark 3"):
                    self.gotFilename(bookmark3)
                    no_plugin = False
                elif pname == _("Filter by Tags"):
                    self.showTagsSelect()
                    no_plugin = False
                elif pname == _("Trailer search"):
                    self.showTrailer()
                    no_plugin = False 
                elif pname == _("Move-Copy"):
                    self.session.open(MovieMove, self, current)
                    no_plugin = False 
                elif pname == _("Rename"):
                    self.session.openWithCallback(self.reload, MovieRetitle, service, current)
                    no_plugin = False 
                elif pname == _("Sort"):
                    if config.movielist.moviesort.value == MovieList.SORT_ALPHANUMERIC:
                        newType = MovieList.SORT_DATE_DESC
                        newCaption = _("Sort by Date (9->1)")
                    else:
                        if config.movielist.moviesort.value == MovieList.SORT_DATE_DESC:
                            newType = MovieList.SORT_DATE_ASC
                            newCaption = _("Sort alphabetically")
                        else:
                            if config.movielist.moviesort.value == MovieList.SORT_DATE_ASC:
                                newType = MovieList.SORT_ALPHANUMERIC
                                newCaption = _("Sort by Date (1->9)")
                    config.movielist.moviesort.value = newType
                    self.setSortType(newType)
                    self.reloadList()
                    if index == 0:
                        self["key_red"].setText(newCaption)
                    elif index == 1:
                        self["key_green"].setText(newCaption)
                    elif index == 2:
                        self["key_yellow"].setText(newCaption)
                    elif index == 3:
                        self["key_blue"].setText(newCaption)
                    no_plugin = False
                else:
                    for p in plugins.getPlugins(where=[PluginDescriptor.WHERE_MOVIELIST]):
                        if pname == str(p.name):
                            plugin = p
                    if plugin is not None:
                        try:
                            plugin(self.session, current)
                            no_plugin = False
                        except:
                            msgText = _("Unknown error!")
                    else: 
                        msgText = _("Plugin not found!")
            else:
                msgText = _("No plugin assigned!")
            if no_plugin:
                self.session.open(MessageBox, msgText, MessageBox.TYPE_INFO)
    
    def reload(self):
        self.reloadList()