import asyncio

import discord

from base import InternedNamedCollection

from chat import ChatService

from .discordchatserver             import DiscordChatServer
from .discordprivatemessagingserver import DiscordPrivateMessagingServer
from .discordmessage                import DiscordMessage

class DiscordChatService(ChatService):
	def __init__(self, name, logger):
		super(DiscordChatService, self).__init__(name, logger)
		
		self.client = discord.Client()
		
		self._privateMessagingServer = DiscordPrivateMessagingServer(self, self.client)
		
		self._servers = InternedNamedCollection(lambda x: DiscordChatServer(self, x) if x != self._privateMessagingServer else self._privateMessagingServer, lambda x: x.id)
		self._servers.inject(self._privateMessagingServer)
		
		self.client.event(self.on_ready)
		self.client.event(self.on_message)
	
	# IChatService
	# Chat Service
	@property
	def isConnected(self):
		return self.client.user is not None
	
	@asyncio.coroutine
	def connect(self, config):
		if self.isConnected: raise RuntimeError("DiscordChatService.connect : Already connected!")
		
		yield from self.client.start(config["email"], config["password"])
	
	@asyncio.coroutine
	def disconnect(self):
		if not self.isConnected: return
		
		yield from self.client.logout()
	
	@property
	def serverCount(self):
		return len(self.servers)
	
	@property
	def servers(self):
		self.updateServers()
		return self._servers
	
	def getServerById(self, id):
		return self.servers.get(id)
	
	def getServerByName(self, name):
		return self.servers.getByName(name)
	
	# DiscordChatService
	@property
	def privateMessagingServer(self):
		return self._privateMessagingServer
	
	# Internal
	def updateServers(self):
		servers = [x for x in self.client.servers]
		servers.append(self.privateMessagingServer)
		self._servers.update(servers)
	
	@asyncio.coroutine
	def on_ready(self):
		self.connected(self)
	
	@asyncio.coroutine
	def on_message(self, message):
		message = DiscordMessage(self, message)
		self.messageReceived(self, message)
		message.server.messageReceived(self, message.server, message)
		message.channel.messageReceived(self, message.channel, message)
