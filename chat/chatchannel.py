import asyncio

from base import Event

from .ichatchannel import IChatChannel

class ChatChannel(IChatChannel):
	def __init__(self, chatService, chatServer):
		super(ChatChannel, self).__init__()
		
		self._chatService = chatService
		self._chatServer  = chatServer
		
		self._messageReceived = Event("messageReceived")
	
	def __str__(self):
		return self.__class__.__name__ + " " + str(self.id) + " " + self.name
	
	# IChatChannel
	# Parent
	@property
	def chatService(self): return self._chatService
	
	@property
	def server(self): return self._chatServer
	
	# Events
	@property
	def messageReceived(self): return self._messageReceived
	
	# Chat Channel
	def postJoin(self, eventLoop = None):
		if eventLoop is None: eventLoop = asyncio.get_event_loop()
		eventLoop.create_task(self.join())
	
	def postMessage(self, content, eventLoop = None):
		if eventLoop is None: eventLoop = asyncio.get_event_loop()
		eventLoop.create_task(self.sendMessage(content))
