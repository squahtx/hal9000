import asyncio

from chat import User

from .discordmessage import DiscordMessage

class DiscordUser(User):
	def __init__(self, chatService, chatServer, user):
		super(DiscordUser, self).__init__(chatService, chatServer)
		
		self.user = user
	
	# IUser
	# Identity
	@property
	def id(self): return self.user.id
	
	@property
	def globalId(self): return "Discord." + self.id
	
	@property
	def displayName(self): return self.user.name
	
	@asyncio.coroutine
	def sendPrivateMessage(self, content):
		message = yield from self.chatService.client.send_message(self.user, content)
		return DiscordMessage(self.chatService, message)
