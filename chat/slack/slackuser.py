import asyncio
import json

from chat import User

class SlackUser(User):
	def __init__(self, chatService, chatServer, user):
		super(SlackUser, self).__init__(chatService, chatServer)
		
		self.user = user
	
	# IUser
	# Identity
	@property
	def id(self): return self.user.id
	
	@property
	def globalId(self): return "Slack." + self.id
	
	@property
	def displayName(self): return self.user.name
	
	# Messages
	@asyncio.coroutine
	def sendPrivateMessage(self, content):
		response = self.chatService.client.api_call("im.open", user = self.id)
		channelId = response.get("channel", {}).get("id")
		if channelId is None: return
		
		return self.server.getChannelById(channelId).sendMessage(content)
