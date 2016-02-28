from ..base import Plugin

class Management(Plugin):
	# Plugin
	def handleInitialize(self):
		self.registerCommand("services", self.handleServices).setDescription("Lists available chat services.")
		self.registerCommand("servers",  self.handleServers).setDescription("Lists available servers.").addParameter("chat service")
		self.registerCommand("channels", self.handleChannels).setDescription("Lists available channels.").addParameter("chat service").addParameter("server name or id")
		self.registerCommand("join",     self.handleJoin).setDescription("Joins a channel").addParameter("chat service").addParameter("server name or id").addParameter("channel name or id")
	
	# Management
	# Internal
	def handleServices(self, command, commandInvocation, message):
		chatServices = [chatService.name for chatService in self.chatbot.chatServices]
		
		message.channel.postMessage("Available chat services: " + ", ".join(chatServices))
	
	def handleServers(self, command, commandInvocation, message):
		chatServiceName = commandInvocation.arguments[0].text
		
		chatService = self.chatbot.getChatService(chatServiceName)
		if chatService is None:
			message.channel.postMessage("Could not find chat service \"" + chatServiceName + "\".")
			return
		
		servers = [server.name + " (" + server.id + ")" for server in chatService.servers]
		servers = sorted(servers)
		
		message.channel.postMessage("Available chat servers: " + "\n    ".join(servers))
	
	def handleChannels(self, command, commandInvocation, message):
		chatServiceName = commandInvocation.arguments[0].text
		serverName      = commandInvocation.arguments[1].text
		
		chatService = self.chatbot.getChatService(chatServiceName)
		if chatService is None:
			message.channel.postMessage("Could not find chat service \"" + chatServiceName + "\".")
			return
		
		server = None
		if server is None: server = chatService.getServerById(serverName)
		if server is None: server = chatService.getServerByName(serverName)
		if server is None:
			message.channel.postMessage("Could not find chat server \"" + serverName + "\".")
			return
		
		channels = [channel.name + " (" + channel.id + ")" for channel in server.channels]
		channels = sorted(channels)
		
		message.channel.postMessage("Available chat channels: " + "\n    ".join(channels))
	
	def handleJoin(self, command, commandInvocation, message):
		chatServiceName = commandInvocation.arguments[0].text
		serverName      = commandInvocation.arguments[1].text
		channelName     = commandInvocation.arguments[2].text
		
		chatService = self.chatbot.getChatService(chatServiceName)
		if chatService is None:
			message.channel.postMessage("Could not find chat service \"" + chatServiceName + "\".")
			return
		
		server = None
		if server is None: server = chatService.getServerById(serverName)
		if server is None: server = chatService.getServerByName(serverName)
		if server is None:
			message.channel.postMessage("Could not find chat server \"" + serverName + "\".")
			return
		
		channel = None
		if channel is None: channel = server.getChannelById(channelName)
		if channel is None: channel = server.getChannelByName(channelName)
		if channel is None:
			message.channel.postMessage("Could not find chat channel \"" + channelName + "\".")
			return
		
		channel.postJoin()
