import asyncio

import slackclient

from base import InternedCollection

from chat import ChatService

from .slackchatserver import SlackChatServer
from .slackmessage    import SlackMessage

class SlackChatService(ChatService):
	def __init__(self, name, logger):
		super(SlackChatService, self).__init__(name, logger)
		
		self.client = None
		self.server = None
	
	# IChatService
	# Chat Service
	@property
	def isConnected(self):
		return self.client is not None
	
	@asyncio.coroutine
	def connect(self, config):
		if self.isConnected: raise RuntimeError("SlackChatService.connect : Already connected!")
		
		self.client = slackclient.SlackClient(config["token"])
		self.client.rtm_connect()
		self.server = SlackChatServer(self, self.client.server)
		
		asyncio.get_event_loop().create_task(self.pollingLoop())
		
		self.connected(self)
	
	@asyncio.coroutine
	def disconnect(self):
		if not self.isConnected: return
		
		self.client = None
	
	@property
	def serverCount(self):
		if self.server is None: return 0
		return 1
	
	@property
	def servers(self):
		if self.server is None: return []
		return [ self.server ]
	
	def getServerById(self, id):
		if self.server is None: return None
		if id == self.server.id: return self.server
		return None
	
	def getServerByName(self, name):
		if self.server is None: return None
		if name == self.server.name: return self.server
		return None
	
	# SlackChatService
	@asyncio.coroutine
	def pollingLoop(self, interval = 1):
		self.log("Started polling loop...")
		
		while self.client is not None:
			events = self.client.rtm_read()
			
			for event in events:
				if event.get("type") != "message": continue
				if event.get("subtype") != None: continue
				
				message = SlackMessage(self, self.server.getChannelById(event["channel"]), event)
				self.messageReceived(self, message)
				message.server.messageReceived(self, message.server, message)
				message.channel.messageReceived(self, message.channel, message)
			
			yield from asyncio.sleep(interval)
