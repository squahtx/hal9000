import asyncio
import time

from chat import Message

class DiscordMessage(Message):
	def __init__(self, chatService, message):
		super(DiscordMessage, self).__init__(chatService)
		
		self.message = message
	
	# IMessage
	# Parent
	@property
	def server(self):
		if self.message.server is None: return self.chatService.privateMessagingServer
		return self.chatService.getServerById(self.message.server.id)
	
	@property
	def channel(self):
		return self.server.channels.intern(self.message.channel)
	
	# Message
	@property
	def author(self):
		return self.server.users.intern(self.message.author)
	
	@property
	def timestamp(self):
		return time.mktime(self.message.timestamp.timetuple())
	
	@property
	def content(self):
		return self.message.content
	
	@property
	def isPrivateMessage(self):
		return self.message.server is None
	
	@asyncio.coroutine
	def editMessage(self, newContent):
		self.message = yield from self.chatService.client.edit_message(self.message, newContent)
		return self
	
	@asyncio.coroutine
	def delete(self):
		yield from self.chatService.client.delete_message(self.message)
