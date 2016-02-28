from base import abstract

class IChatServer(object):
	# Identity
	@property
	@abstract
	def id(self): pass
	
	@property
	@abstract
	def globalId(self): pass
	
	@property
	@abstract
	def name(self): pass
	
	# Parent
	@property
	@abstract
	def chatService(self): pass
	
	# Events
	@property
	@abstract
	def messageReceived(self): pass
	
	# Server
	# Channels
	@property
	@abstract
	def channelCount(self): pass
	
	@property
	@abstract
	def channels(self): pass
	
	@abstract
	def getChannelById(self, id): pass
	
	@abstract
	def getChannelByName(self, name): pass
	
	# Users
	@property
	@abstract
	def userCount(self): pass
	
	@property
	@abstract
	def users(self): pass
	
	@abstract
	def getUserById(self, id): pass
	
	@property
	@abstract
	def localUser(self): pass
