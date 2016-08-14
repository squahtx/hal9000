import asyncio
import json

from chat import ChatChannel

from .slackmessage import SlackMessage

class SlackChatChannel(ChatChannel):
	def __init__(self, chatService, chatServer, channel):
		super(SlackChatChannel, self).__init__(chatService, chatServer)
		
		self.channel = channel
	
	# IChatChannel
	# Identity
	@property
	def id(self): return self.channel.id
	
	@property
	def globalId(self): return self.server.globalId + "." + self.id
	
	@property
	def name(self):
		return self.channel.name
	
	# Chat Channel
	@property
	def isPrivateMessageChannel(self):
		return self.id.startswith("D")
	
	@asyncio.coroutine
	def join(self):
		self.chatService.client.api_call("channels.join", channel = self.id)
	
	@asyncio.coroutine
	def sendMessage(self, message):
		response = self.chatService.client.api_call("chat.postMessage", channel = self.id, text = message, as_user = True)
		if "message" not in response: return None
		return SlackMessage(self.chatService, self, response["message"])
