from Components.GUIComponent import GUIComponent
from Components.VariableText import VariableText
from enigma import eLabel
from ServiceUtils import realSize, diskUsage

class DiskInfo(VariableText, GUIComponent):
	FREE = 0
	USED = 1
	SIZE = 2
	
	def __init__(self, path, type, update = True):
		GUIComponent.__init__(self)
		VariableText.__init__(self)
		self.type = type
		self.path = path
		if update:
			self.update()
	
	def update(self):
		try:
			total, used, free = diskUsage(self.path)
			if self.type == self.FREE:
				self.setText(("%s " + _("free diskspace")) % (realSize(free)))
			if self.type == self.USED:
				self.setText(("%s " + _("used diskspace")) % (realSize(used)))
			if self.type == self.SIZE:
				self.setText(("%s " + _("total diskspace")) % (realSize(total)))
		except OSError:
			return -1

	GUI_WIDGET = eLabel
