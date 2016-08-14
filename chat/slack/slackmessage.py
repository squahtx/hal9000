import asyncio
import json
import time

from chat import Message

class SlackMessage(Message):
	def __init__(self, chatService, channel, message):
		super(SlackMessage, self).__init__(chatService)
		
		self._channel = channel
		self.message = message
	
	# IMessage
	# Parent
	@property
	def server(self):
		return self.chatService.server
	
	@property
	def channel(self):
		return self._channel
	
	# Message
	@property
	def author(self):
		return self.server.getUserById(self.message.get("user"))
	
	@property
	def timestamp(self):
		return time.mktime(float(self.message["ts"]))
	
	@property
	def content(self):
		return self.message["text"]
	
	@property
	def isPrivateMessage(self):
		return self.channel.isPrivateMessageChannel
	
	@asyncio.coroutine
	def editMessage(self, newContent):
		response = self.chatService.client.api_call("chat.update", channel = self.channel.id, ts = self.message["ts"], text = newContent)
		self.message["text"] = response["text"]
		return self
	
	@asyncio.coroutine
	def delete(self):
		self.chatService.client.api_call("chat.delete", channel = self.channel.id, ts = self.message["ts"])
