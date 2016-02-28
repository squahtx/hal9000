import asyncio

from base import abstract

class IChatChannel(object):
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
	
	@property
	@abstract
	def server(self): pass
	
	# Events
	@property
	@abstract
	def messageReceived(self): pass
	
	# Chat Channel
	@property
	@abstract
	def isPrivateMessageChannel(self): pass
	
	@asyncio.coroutine
	@abstract
	def join(self): pass
	
	@abstract
	def postJoin(self, eventLoop = None): pass
	
	@asyncio.coroutine
	@abstract
	def sendMessage(self, content): pass
	
	@abstract
	def postMessage(self, content, eventLoop = None): pass
