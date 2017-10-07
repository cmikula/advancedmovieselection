# -*- coding: utf-8 -*-
from Screens.InputBox import PinInput, InputBox, Input
from Tools.BoundFunction import boundFunction

class PinInputDialog(PinInput, InputBox):
    def __init__(self, session, windowTitle, service, triesEntry = None, pinList = [0, 0, 0, 0], *args, **kwargs):
        InputBox.__init__(self, session = session, windowTitle = windowTitle, maxSize=True, type=Input.PIN, *args, **kwargs)
        PinInput.__init__(self, session = session, service = service, triesEntry = triesEntry, pinList = pinList, *args, **kwargs)
        self.onShown.append(boundFunction(self.setTitle, windowTitle))
