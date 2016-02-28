import asyncio

from base import abstract

class IChatService(object):
	# Events
	@property
	@abstract
	def connected(self): pass
	
	@property
	@abstract
	def messageReceived(self): pass
	
	# Chat Service
	@property
	@abstract
	def name(self): pass
	
	@property
	@abstract
	def isConnected(self): pass
	
	@asyncio.coroutine
	@abstract
	def connect(self, config): pass
	
	@asyncio.coroutine
	@abstract
	def disconnect(self): pass
	
	@abstract
	def postConnect(self, config, eventLoop = None): pass
	
	@abstract
	def postDisconnect(self, eventLoop = None): pass
	
	@property
	@abstract
	def serverCount(self): pass
	
	@property
	@abstract
	def servers(self): pass
	
	@abstract
	def getServerById(self, id): pass
	
	@abstract
	def getServerByName(self, id): pass
