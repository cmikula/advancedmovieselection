#!/usr/bin/python
# -*- coding: utf-8 -*- 
#  Advanced Movie Selection for Dreambox-Enigma2
#
#  The plugin is developed on the basis from a lot of single plugins (thx for the code @ all)
#  Coded by JackDaniel and cmikula (c)2012
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

from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ActionMap import ActionMap, NumberActionMap
from Components.config import config, getConfigListEntry, ConfigText, KEY_0, KEY_TIMEOUT, KEY_NUMBERS
from Components.ConfigList import ConfigListScreen
from Tools.NumericalTextInput import NumericalTextInput
from enigma import eTimer

from Screens.NumericalTextInputHelpDialog import NumericalTextInputHelpDialog
class AdvancedTextInputHelpDialog(NumericalTextInputHelpDialog):
    skin = """
        <screen name="AdvancedTextInputHelpDialog" position="center,480" zPosition="100" size="394,124" backgroundColor="#202020" flags="wfNoBorder">
            <eLabel position="0,0" size="392,122" backgroundColor="#c0c0c0" zPosition="-1" />
            <widget name="key1" position="2,2" size="130,30" font="Regular;18" halign="center" valign="center" />
            <widget name="key2" position="132,2" size="130,30" font="Regular;18" halign="center" valign="center" />
            <widget name="key3" position="262,2" size="130,30" font="Regular;18" halign="center" valign="center" />
            <widget name="key4" position="2,32" size="130,30" font="Regular;18" halign="center" valign="center" />
            <widget name="key5" position="132,32" size="130,30" font="Regular;18" halign="center" valign="center" />
            <widget name="key6" position="262,32" size="130,30" font="Regular;18" halign="center" valign="center" />
            <widget name="key7" position="2,62" size="130,30" font="Regular;18" halign="center" valign="center" />
            <widget name="key8" position="132,62" size="130,30" font="Regular;18" halign="center" valign="center" />
            <widget name="key9" position="262,62" size="130,30" font="Regular;18" halign="center" valign="center" />
            <widget name="help1" position="2,92" size="130,30" font="Regular;18" halign="center" valign="center" />
            <widget name="key0" position="132,92" size="130,30" font="Regular;14" halign="center" valign="center" />
            <widget name="help2" position="262,92" size="130,30" font="Regular;18" halign="center" valign="center" />
        </screen>"""

class AdvancedKeyBoard(VirtualKeyBoard, NumericalTextInput):
    skin = """
        <screen name="AdvancedKeyBoard" position="center,center" size="560,550" zPosition="99" title="Virtual KeyBoard">
            <ePixmap pixmap="skin_default/vkey_text.png" position="9,45" zPosition="-4" size="542,52" alphatest="on"/>
            <widget source="country" render="Pixmap" position="490,0" size="60,40" alphatest="on" borderWidth="2" borderColor="yellow">
            <convert type="ValueToPixmap">LanguageCode</convert>
            </widget>
            <widget name="header" position="10,20" size="500,20" font="Regular;20" transparent="1" noWrap="1"/>
            <widget name="text" position="12,45" size="536,46" font="Regular;46" transparent="1" noWrap="1" halign="right"/>
            <widget name="list" position="10,110" size="540,225" selectionDisabled="1" transparent="1"/>
        </screen>"""
    KEYBOARD = 0x01
    NUM_KEYB = 0x02
    BOTH = KEYBOARD|NUM_KEYB
    def __init__(self, session, title="", text=""):
        VirtualKeyBoard.__init__(self, session, title, text)
        NumericalTextInput.__init__(self, nextFunc=self.nextFunc)
        #self.skinName = "VirtualKeyBoard"
        self.configText = None
        if config.AdvancedMovieSelection.keyboard.value == "virtual":
            use = self.KEYBOARD
        elif config.AdvancedMovieSelection.keyboard.value == "numerical":
            use = self.NUM_KEYB
        else:
            use = self.BOTH
        if not use & self.KEYBOARD:
            # hide the keyboard
            self["list"].hide()
            # overwrite VirtualKeyBoard actions
            # make sure not overwrite any action of base class
            self["actions"] = ActionMap(["OkCancelActions", "WizardActions", "ColorActions", "KeyboardInputActions", "InputBoxActions", "InputAsciiActions"],
            {
                "ok": self.__ok,
                "cancel": self.__cancel,
                "left": self.dummy,
                "right": self.dummy,
                "up": self.dummy,
                "down": self.dummy,
                "red": self.__cancel,
                "green": self.__ok,
                "yellow": self.dummy,
                "deleteBackward": self.dummy,
                "back": self.dummy                
            }, -2)

        if use & self.NUM_KEYB:
            self.timer = eTimer()
            self.timer.callback.append(self.timeout)
            self.configText = ConfigText("", False)
            if text:
                self.configText.text = text
                self.configText.marked_pos = len(text)
            self["config_actions"] = NumberActionMap(["SetupActions", "InputAsciiActions", "KeyboardInputActions"],
            {
                "1": self.keyNumberGlobal,
                "2": self.keyNumberGlobal,
                "3": self.keyNumberGlobal,
                "4": self.keyNumberGlobal,
                "5": self.keyNumberGlobal,
                "6": self.keyNumberGlobal,
                "7": self.keyNumberGlobal,
                "8": self.keyNumberGlobal,
                "9": self.keyNumberGlobal,
                "0": self.keyNumberGlobal
            }, -1) # to prevent left/right overriding the listbox
            
        self.onLayoutFinish.append(self.__onLayoutFinish)
        self.onClose.append(self.__onClose)
    
    def __onLayoutFinish(self):
        if self.configText:
            self.configText.help_window = self.session.instantiateDialog(AdvancedTextInputHelpDialog, self)
            self.configText.help_window.show()
                
    def __onClose(self):
        if self.configText and self.configText.help_window:
            self.session.deleteDialog(self.configText.help_window)
            self.configText.help_window = None
    
    def dummy(self):
        pass
    
    def __ok(self):
        self.close(self["text"].getText())

    def __cancel(self):
        self.close(None)

    def timeout(self):
        self.handleKey(KEY_TIMEOUT)
        self["text"].setMarkedPos(-1)

    def handleKey(self, key):
        if self.configText:
            self.configText.handleKey(key)
            if key in KEY_NUMBERS:
                self.timer.start(1000, 1)

    def keyNumberGlobal(self, number):
        self.handleKey(KEY_0 + number)
        self.getKey(number)
        self.text = self.configText.getText()
        self["text"].setText(self.configText.getText())
        self["text"].setMarkedPos(self.configText.marked_pos)

    def okClicked(self):
        VirtualKeyBoard.okClicked(self)
        self["text"].setMarkedPos(-1)
        if self.configText:
            self.configText.text = self.text
            self.configText.marked_pos = len(self.text)

    def nextFunc(self):
        self["text"].setMarkedPos(-1)
