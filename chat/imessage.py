import asyncio

from base import abstract

class IMessage(object):
	# Parent
	@property
	@abstract
	def chatService(self): pass
	
	@property
	@abstract
	def server(self): pass
	
	@property
	@abstract
	def channel(self): pass
	
	# Message
	@property
	@abstract
	def author(self): pass
	
	@property
	@abstract
	def timestamp(self): pass
	
	@property
	@abstract
	def content(self): pass
	
	@property
	@abstract
	def isPrivateMessage(self): pass
	
	@asyncio.coroutine
	@abstract
	def editMessage(self, newContent): pass
	
	@abstract
	def postEditMessage(self, newContent, eventLoop = None): pass
	
	@asyncio.coroutine
	@abstract
	def delete(self): pass
	
	@abstract
	def postDelete(self, eventLoop = None): pass
