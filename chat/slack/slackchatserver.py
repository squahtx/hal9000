from base import InternedCollection
from base import InternedNamedCollection

from chat import ChatServer

from .slackchatchannel import SlackChatChannel
from .slackuser        import SlackUser

class SlackChatServer(ChatServer):
	def __init__(self, chatService, server):
		super(SlackChatServer, self).__init__(chatService)
		
		self.server = server
		
		self._channels = InternedNamedCollection(lambda x: SlackChatChannel(self.chatService, self, x), lambda x: x.id)
		self._users    = InternedCollection(lambda x: SlackUser(self.chatService, self, x), lambda x: x.id)
	
	# IServer
	# Identity
	@property
	def id(self): return self.server.domain
	
	@property
	def globalId(self): return "Slack." + self.id
	
	@property
	def name(self): return self.id
	
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
		self.updateUsers()
		return self._users
	
	def getUserById(self, id):
		return self.users.get(id)
	
	@property
	def localUser(self):
		return self.getUserById(self.server.login_data["self"]["id"])
	
	# SlackChatServer
	# Internal
	def updateChannels(self):
		self._channels.update(self.server.channels)
	
	def updateUsers(self):
		self._users.update(self.server.users)
