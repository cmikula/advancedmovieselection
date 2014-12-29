'''
Created on 15.12.2014

@author: cmi
'''

from enigma import gFont, ePoint, eSize
from skin import parseColor, parseFont, parseSize, parsePosition
from Tools.Directories import resolveFilename, SCOPE_SKIN
import xml.etree.cElementTree
from os import path
from Components.config import config

class SkinLoader():
    def __init__(self):
        self.load()
    
    def load(self):
        self.dom_skins = []
        self.loadSkin(config.skin.primary_skin.value)

    def loadSkin(self, name, scope=SCOPE_SKIN):
        # read the skin
        filename = resolveFilename(scope, name)
        mpath = path.dirname(filename) + "/"
        self.dom_skins.append((mpath, xml.etree.cElementTree.parse(filename).getroot()))

skin_node = None

class SkinParam():
    def __init__(self, node="MovieList"):
        self.node_name = node
        self.scale = ((1, 1), (1, 1))
        
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


class MovieListSkinParam(SkinParam):
    def __init__(self):
        SkinParam.__init__(self, "MovieList")
        self.listType0_Font0 = gFont("Regular", 22)
        self.listType0_Font1 = gFont("Regular", 19)
        self.listType0_Font2 = gFont("Regular", 16)
        self.listType0_ListHeight = 78

        self.listType1_Font0 = gFont("Regular", 20)
        self.listType1_Font1 = gFont("Regular", 14)
        self.listType1_ListHeight = 39
        
        self.listType2_Font0 = gFont("Regular", 18)
        self.listType2_Font1 = gFont("Regular", 14)
        self.listType2_ListHeight = 26
        
        self.listType3_Font0 = gFont("Regular", 20)
        self.listType3_Font1 = gFont("Regular", 16)
        self.listType3_ListHeight = 26
        self.loadSkinData()
    
    def redrawList(self):
        from MovieList import MovieList
        if self.list_type == MovieList.LISTTYPE_ORIGINAL or self.list_type == MovieList.LISTTYPE_EXTENDED:
            self.l.setFont(0, self.listType0_Font0)
            self.l.setFont(1, self.listType0_Font1)
            self.l.setFont(2, self.listType0_Font2)
            self.l.setItemHeight(self.listType0_ListHeight)
            
            self.f0y = 0
            self.f0h = self.listType0_Font0.pointSize + 5
            self.f1y = self.listType0_Font0.pointSize + 3
            self.f1h = self.listType0_Font1.pointSize + 5
        elif self.list_type == MovieList.LISTTYPE_COMPACT_DESCRIPTION or self.list_type == MovieList.LISTTYPE_COMPACT:
            self.l.setFont(0, self.listType1_Font0)
            self.l.setFont(1, self.listType1_Font1)
            self.l.setItemHeight(self.listType1_ListHeight)

            self.f0y = 0
            self.f0h = self.listType1_Font0.pointSize + 5
            self.f1y = self.listType1_Font0.pointSize + 3
            self.f1h = self.listType1_Font1.pointSize + 5
        elif self.list_type == MovieList.LISTTYPE_MINIMAL_AdvancedMovieSelection:
            self.l.setFont(0, self.listType2_Font0)
            self.l.setFont(1, self.listType2_Font1)
            self.l.setItemHeight(self.listType2_ListHeight)
            
            self.f0y = 0
            self.f0h = self.listType2_Font0.pointSize + 5
            self.f1y = self.listType2_Font0.pointSize + 3
            self.f1h = self.listType2_Font1.pointSize + 5
        else:
            self.l.setFont(0, self.listType3_Font0)
            self.l.setFont(1, self.listType3_Font1)
            self.l.setItemHeight(self.listType3_ListHeight)
            
            self.f0y = 0
            self.f0h = self.listType3_Font0.pointSize + 5
            self.f1y = self.listType3_Font0.pointSize + 3
            self.f1h = self.listType3_Font1.pointSize + 5
        
        self.f2y = self.listType0_Font1.pointSize + 3 + self.f1y
        self.f2h = self.listType0_Font2.pointSize + 5
    
    def parseAttribute(self, attrib, value):
        if attrib == "listType0_Font0":
            self.listType0_Font0 = parseFont(value, self.scale)
        elif attrib == "listType0_Font1":
            self.listType0_Font1 = parseFont(value, self.scale)
        elif attrib == "listType0_Font2":
            self.listType0_Font2 = parseFont(value, self.scale)
        elif attrib == "listType0_ListHeight":
            self.listType0_ListHeight = int(value)

        elif attrib == "listType1_Font0":
            self.listType1_Font0 = parseFont(value, self.scale)
        elif attrib == "listType1_Font1":
            self.listType1_Font1 = parseFont(value, self.scale)
        elif attrib == "listType1_ListHeight":
            self.listType1_ListHeight = int(value)

        elif attrib == "listType2_Font0":
            self.listType2_Font0 = parseFont(value, self.scale)
        elif attrib == "listType2_Font1":
            self.listType2_Font1 = parseFont(value, self.scale)
        elif attrib == "listType2_ListHeight":
            self.listType2_ListHeight = int(value)

        elif attrib == "listType3_Font0":
            self.listType3_Font0 = parseFont(value, self.scale)
        elif attrib == "listType3_Font1":
            self.listType3_Font1 = parseFont(value, self.scale)
        elif attrib == "listType3_ListHeight":
            self.listType3_ListHeight = int(value)

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
        
        self.f0h = self.font0.pointSize + 5
        self.f1h = self.font1.pointSize + 5
        self.f2h = self.font2.pointSize + 5
    
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
        self.line2Pos = ePoint(100, 30)
        self.picPos = ePoint(0, 1)
        self.picSize = eSize(92, 138)
        self.loadSkinData()
    
    def redrawList(self):
        self.l.setFont(0, self.font0)
        self.l.setFont(1, self.font1)
        self.l.setItemHeight(self.listHeight)

        self.f0h = self.font0.pointSize + 5
    
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
        self.line3Pos = ePoint(5, 52)
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
        
        self.f0h = self.font0.pointSize + 5
        self.f1h = self.font1.pointSize + 5
    
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
