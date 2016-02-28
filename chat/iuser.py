import asyncio

from base import abstract

class IUser(object):
	# Identity
	@property
	@abstract
	def id(self): pass
	
	@property
	@abstract
	def globalId(self): pass
	
	@property
	@abstract
	def displayName(self): pass
	
	# Parent
	@property
	@abstract
	def chatService(self): pass
	
	@property
	@abstract
	def server(self): pass
	
	# Messages
	@asyncio.coroutine
	@abstract
	def sendPrivateMessage(self, content): pass
	
	@abstract
	def postPrivateMessage(self, content, eventLoop = None): pass
