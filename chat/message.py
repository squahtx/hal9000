import asyncio

from base import Event

from .imessage import IMessage

class Message(IMessage):
	def __init__(self, chatService):
		super(Message, self).__init__()
		
		self._chatService = chatService
	
	# IMessage
	# Parent
	@property
	def chatService(self): return self._chatService
	
	# Message
	def postEditMessage(self, newContent, eventLoop = None):
		if eventLoop is None: eventLoop = asyncio.get_event_loop()
		eventLoop.create_task(self.editMessage(newContent))
	
	def postDelete(self, eventLoop = None):
		if eventLoop is None: eventLoop = asyncio.get_event_loop()
		eventLoop.create_task(self.delete())
