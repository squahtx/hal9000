import asyncio

from base import Event

from .iuser import IUser

class User(IUser):
	def __init__(self, chatService, chatServer):
		super(User, self).__init__()
		
		self._chatService = chatService
		self._chatServer = chatServer
	
	def __str__(self):
		return self.__class__.__name__ + " " + str(self.id) + " " + self.name
	
	# IUser
	# Parent
	@property
	def chatService(self): return self._chatService
	
	@property
	def server(self): return self._chatServer
	
	# Messages
	def postPrivateMessage(self, content, eventLoop = None):
		if eventLoop is None: eventLoop = asyncio.get_event_loop()
		eventLoop.create_task(self.sendPrivateMessage(content))
