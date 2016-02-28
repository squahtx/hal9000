from base import InternedCollection
from base import InternedNamedCollection

from chat import ChatServer

from .discordchatchannel import DiscordChatChannel
from .discorduser        import DiscordUser

class DiscordPrivateMessagingServer(ChatServer):
	def __init__(self, chatService, client):
		super(DiscordPrivateMessagingServer, self).__init__(chatService)
		
		self.client = client
		
		self._channels = InternedNamedCollection(lambda x: DiscordChatChannel(self.chatService, self, x), lambda x: x.id)
		self._users    = InternedCollection(lambda x: DiscordUser(self.chatService, self, x), lambda x: x.id)
	
	# IServer
	# Identity
	@property
	def id(self): return "PM"
	
	@property
	def globalId(self): return "Discord." + self.id
	
	@property
	def name(self): return "Private Messages"
	
	# Server
	# Channels
	@property
	def channelCount(self):
		return len(self.channels)
	
	@property
	def channels(self):
		self.updateChannels()
		return self._channels
	
	def getChannelById(self, id):
		return self.channels.get(id)
	
	def getChannelByName(self, name):
		return self.channels.getByName(name)
	
	# Users
	@property
	def userCount(self):
		return len(self.users)
	
	@property
	def users(self):
		return self._users
	
	def getUserById(self, id):
		return self.usersById.get(id)
	
	@property
	def localUser(self):
		return self.users.intern(self.client.user)
	
	# DiscordPrivateMessagingServer
	# Internal
	def updateChannels(self):
		self._channels.update(self.client.private_channels)
