from base import abstract

class IChatBot(object):
	# Events
	@property
	def messageReceived(self): pass
	
	# Chat Bot
	@property
	@abstract
	def running(self): pass
	
	@property
	@abstract
	def commandSystem(self): pass
	
	@abstract
	def run(self): pass
	
	# Plugins
	@abstract
	def addPlugin(self, plugin): pass
	
	@abstract
	def removePlugin(self, plugin): pass
