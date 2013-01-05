from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ
import gettext
from skin import loadSkin

def callerName():
    import inspect
    frame=inspect.currentframe()
    frame=frame.f_back.f_back
    code=frame.f_code
    return code.co_filename

def localeInit():
    print "[AdvancedMovieSelection] initialize..."
    loadSkin(resolveFilename(SCOPE_PLUGINS) + "Extensions/AdvancedMovieSelection/skin/skin.xml")
    language.addCallback(localeInit)
    lang = language.getLanguage()
    environ["LANGUAGE"] = lang[:2]
    gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
    gettext.textdomain("enigma2")
    gettext.bindtextdomain("AdvancedMovieSelection", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/AdvancedMovieSelection/locale/"))

    ln = language.lang[language.activeLanguage][1]
    from AboutParser import AboutParser
    AboutParser.setLocale(ln)
    from MovieDB import tmdb, tvdb
    tmdb.setLocale(ln)
    tvdb.setLocale(ln)

def _(txt):
    t = gettext.dgettext("AdvancedMovieSelection", txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t
