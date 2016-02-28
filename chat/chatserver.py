from base import Event

from .ichatserver import IChatServer

class ChatServer(IChatServer):
	def __init__(self, chatService):
		super(ChatServer, self).__init__()
		
		self._chatService = chatService
		
		self._messageReceived = Event("messageReceived")
	
	def __str__(self):
		return self.__class__.__name__ + " " + str(self.id) + " " + self.name
	
	# IChatServer
	# Parent
	@property
	def chatService(self): return self._chatService
	
	# Events
	@property
	def messageReceived(self): return self._messageReceived
