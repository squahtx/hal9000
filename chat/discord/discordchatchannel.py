import asyncio

from chat import ChatChannel

from .discordmessage import DiscordMessage

class DiscordChatChannel(ChatChannel):
	def __init__(self, chatService, chatServer, channel):
		super(DiscordChatChannel, self).__init__(chatService, chatServer)
		
		self.channel = channel
	
	# IChatChannel
	# Identity
	@property
	def id(self): return self.channel.id
	
	@property
	def globalId(self): return self.server.globalId + "." + self.id
	
	@property
	def name(self):
		if self.isPrivateMessageChannel: return self.id
		return self.channel.name
	
	# Chat Channel
	@property
	def isPrivateMessageChannel(self):
		return not hasattr(self.channel, "name")
	
	@asyncio.coroutine
	def join(self, message):
		return
	
	@asyncio.coroutine
	def sendMessage(self, content):
		message = yield from self.chatService.client.send_message(self.channel, content)
		return DiscordMessage(self.chatService, message)
