from Screens.MessageBox import MessageBox 

class MessageBoxEx(MessageBox):
    def __init__(self, session, text, type=MessageBox.TYPE_YESNO, timeout= -1, close_on_any_key=False, default=True, enable_input=True, msgBoxID=None):
        MessageBox.__init__(self, session, text, type=type, timeout=timeout, close_on_any_key=close_on_any_key, default=default, enable_input=enable_input, msgBoxID=msgBoxID)
        self.skinName = "MessageBox"

    def cancel(self):
        self.close(None)
