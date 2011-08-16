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
        if pname == _("Home"):
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
        else:
            for p in plugins.getPlugins(where=[PluginDescriptor.WHERE_MOVIELIST]):
                if pname == str(p.name):
                    if config.AdvancedMovieSelection.buttoncaption.value == "1":
                        return p.description
                    else:
                        return p.name
        return pname
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
        self.startPlugin(str(config.AdvancedMovieSelection.red.value), self["key_red"])
    
    def greenpressed(self):
        self.startPlugin(str(config.AdvancedMovieSelection.green.value), self["key_green"])
    
    def yellowpressed(self):
        self.startPlugin(str(config.AdvancedMovieSelection.yellow.value), self["key_yellow"])
    
    def bluepressed(self):
        self.startPlugin(str(config.AdvancedMovieSelection.blue.value), self["key_blue"])
    
    def startPlugin(self, pname, key_number):
        home = config.AdvancedMovieSelection.homepath.value
        bookmark1 = config.AdvancedMovieSelection.bookmark1path.value
        bookmark2 = config.AdvancedMovieSelection.bookmark2path.value
        bookmark3 = config.AdvancedMovieSelection.bookmark3path.value
        plugin = None
        errorText = None
        current = self.getCurrent()
        service = self.getCurrent()
        if current is not None:
            if pname != _("Nothing"):
                if pname == _("Delete"):
                    if not (service.flags):
                        self.delete()
                    else:
                        self.session.open(MessageBox, _("You cannot delete this!"), MessageBox.TYPE_ERROR)
                elif pname == _("Home"):
                    self.gotFilename(home)
                elif pname == _("Bookmark(s) on/off"):
                    config.AdvancedMovieSelection.show_bookmarks.value = not config.AdvancedMovieSelection.show_bookmarks.value
                    self.reload()
                elif pname == _("Bookmark 1"):
                    self.gotFilename(bookmark1)
                elif pname == _("Bookmark 2"):
                    self.gotFilename(bookmark2)
                elif pname == _("Bookmark 3"):
                    self.gotFilename(bookmark3)
                elif pname == _("Filter by Tags"):
                    self.showTagsSelect()
                elif pname == _("Trailer search"):
                    self.showTrailer()
                elif pname == _("Move-Copy"):
                    self.session.open(MovieMove, self, current)
                elif pname == _("Rename"):
                    self.session.openWithCallback(self.reload, MovieRetitle, service, current)
                elif pname == _("TMDb search & D/L"):
                    if not (service.flags):
                        from SearchTMDb import TMDbMain as TMDbMainsave
                        from ServiceProvider import ServiceCenter
                        searchTitle = ServiceCenter.getInstance().info(service).getName(service)
                        self.session.openWithCallback(self.reload, TMDbMainsave, searchTitle, service)
                    else:
                        self.session.open(MessageBox, _("TMDb search here not possible, please select a movie !"), MessageBox.TYPE_INFO)
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
                    key_number.setText(newCaption)
                else:
                    for p in plugins.getPlugins(where=[PluginDescriptor.WHERE_MOVIELIST]):
                        if pname == str(p.name):
                            plugin = p
                    if plugin is not None:
                        try:
                            plugin(self.session, current)
                        except:
                            errorText = _("Unknown error!")
                    else: 
                        errorText = _("Plugin not found!")
            else:
                errorText = _("No plugin assigned!")
            if errorText:
                self.session.open(MessageBox, errorText, MessageBox.TYPE_INFO)
    
    def reload(self, retval = None):
        self.reloadList()