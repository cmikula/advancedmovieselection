'''
Created on 15.12.2014

@author: cmi
'''

from enigma import gFont, ePoint, eSize
from skin import parseFont, parseSize, parsePosition, parseColor
from Tools.Directories import resolveFilename, fileExists, SCOPE_SKIN, SCOPE_CONFIG
from Components.config import config
import os, xml.etree.cElementTree

class SkinLoader():
    def __init__(self):
        self.load()
    
    def load(self):
        self.dom_skins = []
        self.loadSkin('skin_user.xml', SCOPE_CONFIG)
        self.loadSkin(config.skin.primary_skin.value)

    def loadSkin(self, name, scope=SCOPE_SKIN):
        # read the skin
        filename = resolveFilename(scope, name)
        if fileExists(filename):
            mpath = os.path.dirname(filename) + "/"
            self.dom_skins.append((mpath, xml.etree.cElementTree.parse(filename).getroot()))
            return True
        return False

skin_node = None

class SkinParam():
    def __init__(self, node="MovieList"):
        self.node_name = node
        self.scale = ((1, 1), (1, 1))
        self.renderer_extend = 10
                
    def loadSkinData(self):
        if skin_node is False:
            print "[AdvancedMovieSelection] load skin disabled"
            self.redrawList()
            return
        if skin_node is None:
            print "[AdvancedMovieSelection] load skin data"
            skinLoader = SkinLoader()
            skinLoader.load()
            skins = skinLoader.dom_skins[:]
            skins.reverse()
            for (path, dom_skin) in skins:
                self.findSkinData(dom_skin, path)
        if skin_node is not None:
            self.parseNode(skin_node)
        else:
            global skin_node
            skin_node = False
        self.redrawList()

        allways_reload_skin = False
        if allways_reload_skin:
            global skin_node
            skin_node = None

    def findSkinData(self, skin, path_prefix):
        for node in skin.findall("screen"):
            if not node.attrib.get('name', '') == "AdvancedMovieListSkinExtension":
                continue
            global skin_node
            skin_node = node
        
    def parseNode(self, node):
        print "[AdvancedMovieSelection] parse node", self.node_name
        for n in node.findall(self.node_name):
            for a in n.items():
                attrib = a[0]
                value = a[1]
                self.parseAttribute(attrib, value)
    
    def parseAttribute(self, attrib, value):
        pass
    
    def getTextRendererWidth(self):
        return self.textRenderer.calculateSize().width() + self.renderer_extend

class MovieListSkinParam(SkinParam):
    def __init__(self):
        SkinParam.__init__(self, "MovieList")
        self.list3_Font1 = gFont("Regular", 22)
        self.list3_Font2 = gFont("Regular", 20)
        self.list3_TextPos = 78
        self.list3_ListHeight = 78
        self.list3_Progress = (50, 8, 1, 60)
        self.list3Pos1 = 0
        self.list3Pos2 = 26
        self.list3Pos3 = 52

        self.list2_Font1 = gFont("Regular", 18)
        self.list2_Font2 = gFont("Regular", 15)
        self.list2_ListHeight = 39
        self.list2_Progress = (50, 8, 1, 26)
        self.list2Pos1 = 0
        self.list2Pos2 = 22
        
        self.list1_Font1 = gFont("Regular", 20)
        self.list1_Font2 = gFont("Regular", 15)
        self.list1_ListHeight = 26
        self.list1_Progress = (50, 8, 1, 8)
        self.list1Pos1 = 0
        
        self.icon_size = 20
        
        self.colorSel1 = None
        self.colorSel2 = None
        self.color1 = None
        self.color2 = None
        self.colorWatching = None
        self.colorFinished = None
        self.colorRecording = None
        self.colorMark = None
        
        self.loadSkinData()
    
    def redrawList(self):
        from MovieList import MovieList
        if self.list_type == MovieList.LISTTYPE_ORIGINAL or self.list_type == MovieList.LISTTYPE_EXTENDED:
            self.font1 = self.list3_Font1
            self.font2 = self.list3_Font2
            self.l.setItemHeight(self.list3_ListHeight)
            
            self.line1y = self.list3Pos1
            self.line2y = self.list3Pos2
            self.line3y = self.list3Pos3
            self.progress = self.list3_Progress
        elif self.list_type == MovieList.LISTTYPE_COMPACT_DESCRIPTION or self.list_type == MovieList.LISTTYPE_COMPACT:
            self.font1 = self.list2_Font1
            self.font2 = self.list2_Font2
            self.l.setItemHeight(self.list2_ListHeight)

            self.line1y = self.list2Pos1
            self.line2y = self.list2Pos2
            self.progress = self.list2_Progress
        else:
            self.font1 = self.list1_Font1
            self.font2 = self.list1_Font2
            self.l.setItemHeight(self.list1_ListHeight)
            
            self.line1y = self.list1Pos1
            self.progress = self.list1_Progress

        self.l.setFont(0, self.font1)
        self.l.setFont(1, self.font2)
    
    def parseAttribute(self, attrib, value):
        if attrib == "list3_Font1":
            self.list3_Font1 = parseFont(value, self.scale)
        elif attrib == "list3_Font2":
            self.list3_Font2 = parseFont(value, self.scale)
        elif attrib == "list3_ListHeight":
            self.list3_ListHeight = int(value)
        elif attrib == "list3_TextPos":
            self.list3_TextPos = int(value)
        elif attrib == "list3Pos":
            v = value.split(',')
            self.list3Pos1 = int(v[0])
            self.list3Pos2 = int(v[1])
            self.list3Pos3 = int(v[2])

        elif attrib == "list2_Font1":
            self.list2_Font1 = parseFont(value, self.scale)
        elif attrib == "list2_Font2":
            self.list2_Font2 = parseFont(value, self.scale)
        elif attrib == "list2_ListHeight":
            self.list2_ListHeight = int(value)
        elif attrib == "list2Pos":
            v = value.split(',')
            self.list2Pos1 = int(v[0])
            self.list2Pos2 = int(v[1])

        elif attrib == "list1_Font1":
            self.list1_Font1 = parseFont(value, self.scale)
        elif attrib == "list1_Font2":
            self.list1_Font2 = parseFont(value, self.scale)
        elif attrib == "list1_ListHeight":
            self.list1_ListHeight = int(value)
        elif attrib == "list1Pos":
            v = value.split(',')
            self.list1Pos1 = int(v[0])

        elif attrib == "list1_Progress":
            v = value.split(',')
            self.list1_Progress = (int(v[0]), int(v[1]), int(v[2]), int(v[3]))
        elif attrib == "list2_Progress":
            v = value.split(',')
            self.list2_Progress = (int(v[0]), int(v[1]), int(v[2]), int(v[3]))
        elif attrib == "list3_Progress":
            v = value.split(',')
            self.list3_Progress = (int(v[0]), int(v[1]), int(v[2]), int(v[3]))
        elif attrib == "renderer_extend":
            self.renderer_extend = int(value)

        elif attrib == "icon_size":
            self.icon_size = int(value)

        elif attrib == "color1":
            self.color1 = parseColor(value).argb()
        elif attrib == "color2":
            self.color2 = parseColor(value).argb()
        elif attrib == "colorSel1":
            self.colorSel1 = parseColor(value).argb()
        elif attrib == "colorSel2":
            self.colorSel2 = parseColor(value).argb()
        elif attrib == "colorWatching":
            self.colorWatching = parseColor(value).argb()
        elif attrib == "colorFinished":
            self.colorFinished = parseColor(value).argb()
        elif attrib == "colorRecording":
            self.colorRecording = parseColor(value).argb()
        elif attrib == "colorMark":
            self.colorMark = parseColor(value).argb()

class WastebasketSkinParam(SkinParam):
    def __init__(self):
        SkinParam.__init__(self, "Wastebasket")
        self.font0 = gFont("Regular", 20)
        self.font1 = gFont("Regular", 18)
        self.font2 = gFont("Regular", 16)
        self.listHeight = 75
        self.line1Pos = ePoint(5, 2)
        self.line2Pos = ePoint(5, 29)
        self.line3Pos = ePoint(5, 54)
        self.line1Split = 200
        self.line2Split = 200
        self.line3Split = 300
        self.loadSkinData()
    
    def redrawList(self):
        self.l.setFont(0, self.font0)
        self.l.setFont(1, self.font1)
        self.l.setFont(2, self.font2)
        self.l.setItemHeight(self.listHeight)
        
        self.f0h = self.font0.pointSize + 7
        self.f1h = self.font1.pointSize + 7
        self.f2h = self.font2.pointSize + 7
    
    def parseAttribute(self, attrib, value):
        if attrib == "font0":
            self.font0 = parseFont(value, self.scale)
        elif attrib == "font1":
            self.font1 = parseFont(value, self.scale)
        elif attrib == "font2":
            self.font2 = parseFont(value, self.scale)
        elif attrib == "listHeight":
            self.listHeight = int(value)
        elif attrib == "line1Pos":
            self.line1Pos = parsePosition(value, self.scale)
        elif attrib == "line2Pos":
            self.line2Pos = parsePosition(value, self.scale)
        elif attrib == "line3Pos":
            self.line3Pos = parsePosition(value, self.scale)
        elif attrib == "line1Split":
            self.line1Split = int(value)
        elif attrib == "line2Split":
            self.line2Split = int(value)
        elif attrib == "line3Split":
            self.line3Split = int(value)

class TMDbSkinParam(SkinParam):
    def __init__(self, node="TMDb"):
        SkinParam.__init__(self, node)
        self.font0 = gFont("Regular", 20)
        self.font1 = gFont("Regular", 18)
        self.listHeight = 140
        self.line1Pos = ePoint(100, 5)
        self.line2Pos = ePoint(100, 33)
        self.picPos = ePoint(0, 1)
        self.picSize = eSize(92, 138)
        self.loadSkinData()
    
    def redrawList(self):
        self.l.setFont(0, self.font0)
        self.l.setFont(1, self.font1)
        self.l.setItemHeight(self.listHeight)

        self.f0h = self.font0.pointSize + 7
    
    def parseAttribute(self, attrib, value):
        if attrib == "font0":
            self.font0 = parseFont(value, self.scale)
        elif attrib == "font1":
            self.font1 = parseFont(value, self.scale)
        elif attrib == "listHeight":
            self.listHeight = int(value)
        elif attrib == "line1Pos":
            self.line1Pos = parsePosition(value, self.scale)
        elif attrib == "line2Pos":
            self.line2Pos = parsePosition(value, self.scale)
        elif attrib == "picPos":
            self.picPos = parsePosition(value, self.scale)
        elif attrib == "picSize":
            self.picSize = parseSize(value, self.scale)

class TVDbSerieSkinParam(TMDbSkinParam):
    def __init__(self):
        TMDbSkinParam.__init__(self, "TVDbSerie")

class TVDbEpisodeSkinParam(TMDbSkinParam):
    def __init__(self):
        TMDbSkinParam.__init__(self, "TVDbEpisode")
        self.line1Pos = ePoint(5, 2)
        self.line2Pos = ePoint(5, 27)
        self.line3Pos = ePoint(5, 54)
        self.loadSkinData()

    def parseAttribute(self, attrib, value):
        TMDbSkinParam.parseAttribute(self, attrib, value)
        if attrib == "line3Pos":
            self.line3Pos = parsePosition(value, self.scale)

class MoveCopyProgressSkinParam(SkinParam):
    def __init__(self):
        SkinParam.__init__(self, "MoveCopyProgress")
        self.font0 = gFont("Regular", 20)
        self.font1 = gFont("Regular", 16)
        self.listHeight = 155
        self.line1Pos = ePoint(5, 9)
        self.line2Pos = ePoint(5, 32)
        self.line3Pos = ePoint(5, 52)
        self.line4Pos = ePoint(5, 72)
        self.line5Pos = ePoint(5, 92)
        self.line6Pos = ePoint(5, 112)
        self.line7Pos = ePoint(5, 132)
        self.progressPos = ePoint(5, 2)
        self.progressHeight = 5
        self.lineSplit = 180
        self.loadSkinData()
    
    def redrawList(self):
        self.l.setFont(0, self.font0)
        self.l.setFont(1, self.font1)
        self.l.setItemHeight(self.listHeight)
        
        self.f0h = self.font0.pointSize + 7
        self.f1h = self.font1.pointSize + 7
    
    def parseAttribute(self, attrib, value):
        if attrib == "font0":
            self.font0 = parseFont(value, self.scale)
        elif attrib == "font1":
            self.font1 = parseFont(value, self.scale)
        elif attrib == "listHeight":
            self.listHeight = int(value)
        elif attrib == "line1Pos":
            self.line1Pos = parsePosition(value, self.scale)
        elif attrib == "line2Pos":
            self.line2Pos = parsePosition(value, self.scale)
        elif attrib == "line3Pos":
            self.line3Pos = parsePosition(value, self.scale)
        elif attrib == "line4Pos":
            self.line4Pos = parsePosition(value, self.scale)
        elif attrib == "line5Pos":
            self.line5Pos = parsePosition(value, self.scale)
        elif attrib == "line6Pos":
            self.line6Pos = parsePosition(value, self.scale)
        elif attrib == "line7Pos":
            self.line7Pos = parsePosition(value, self.scale)
        elif attrib == "lineSplit":
            self.lineSplit = int(value)
        elif attrib == "progressPos":
            self.progressPos = parsePosition(value, self.scale)
        elif attrib == "progressHeight":
            self.progressHeight = int(value)

class AboutSkinParam(SkinParam):
    def __init__(self):
        SkinParam.__init__(self, "AboutVersionList")
        self.font = gFont("Regular", 20)
        self.listHeight = 30
        self.loadSkinData()
    
    def redrawList(self):
        self.l.setFont(0, self.font)
        self.l.setItemHeight(self.listHeight)
        
        self.fh = self.font.pointSize + 7
    
    def parseAttribute(self, attrib, value):
        if attrib == "font":
            self.font = parseFont(value, self.scale)
        elif attrib == "listHeight":
            self.listHeight = int(value)
