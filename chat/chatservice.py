from base import Event

from .ichatservice import IChatService

class ChatService(IChatService):
	def __init__(self, name, logger):
		super(ChatService, self).__init__()
		
		self._name = name
		self._logger = logger
		
		self._connected = Event("connected")
		self._messageReceived = Event("messageReceived")
	
	# IChatService
	# Events
	@property
	def connected(self): return self._connected
	
	@property
	def messageReceived(self): return self._messageReceived
	
	# Chat Service
	def postConnect(self, config, eventLoop = None):
		if eventLoop is None: eventLoop = asyncio.get_event_loop()
		eventLoop.create_task(self.connect(config))
	
	def postDisconnect(self, eventLoop = None):
		if eventLoop is None: eventLoop = asyncio.get_event_loop()
		eventLoop.create_task(self.disconnect())
	
	# ChatService
	@property
	def name(self):
		return self._name
	
	@property
	def logger(self):
		return self._logger
	
	def log(self, message):
		if self.logger is None: return
		
		self.logger.log("[" + self.__class__.__name__ + "] " + message)
