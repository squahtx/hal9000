import asyncio
import traceback

from base         import Event

from .ichatbot    import IChatBot

from .logging     import MulticastLogger
from .logging     import ChannelLogger
from .logging     import ConsoleLogger

from .commands    import CommandSystem

from chat.discord import DiscordChatService
from chat.slack   import SlackChatService

class ChatBot(IChatBot):
	def __init__(self):
		super(ChatBot, self).__init__()
		
		self._connected       = Event("connected")
		self._messageReceived = Event("messageReceived")
		
		self.config = None
		
		self._running = False
		self._eventLoop = None
		
		self.logger = MulticastLogger()
		self.logger.add(ConsoleLogger())
		self.channelLoggers = []
		
		self.plugins = {}
		self._commandSystem = CommandSystem(self.logger)
		
		self.chatServiceFactories = {}
		self.chatServiceFactories["Discord"] = DiscordChatService
		self.chatServiceFactories["Slack"]   = SlackChatService
		
		self._chatServices = {}
	
	# IChatBot
	# Events
	@property
	def connected(self):
		return self._connected
	
	@property
	def messageReceived(self):
		return self._messageReceived
	
	# Chat Bot
	@property
	def running(self):
		return self._running
	
	@property
	def commandSystem(self):
		return self._commandSystem
	
	def run(self, config, eventLoop = None):
		if eventLoop is None: eventLoop = asyncio.get_event_loop()
		
		if self._running: raise RuntimeException("ChatBot.run : ChatBot is already running!")
		
		self._running   = True
		self._eventLoop = eventLoop
		
		self.config = config
		
		# Logging
		for loggerConfig in config.logging.get("destinations", []):			
			channelLogger = ChannelLogger()
			self.channelLoggers.append(channelLogger)
			self.logger.add(channelLogger)
		
		self.logger.log("Chatbot starting...")
		
		# Chat services
		for chatServiceName, chatServiceConfig in self.config.services.items():
			if not chatServiceConfig.get("enabled", True):
				self.logger.log("    Skipping disabled chat service \"" + chatServiceName + "\".")
				continue
			
			chatService = self.chatServiceFactories[chatServiceConfig["type"]](chatServiceName, self.logger)
			self._chatServices[chatServiceName] = chatService
			
			chatService.connected.addListener(self.handleConnected)
			chatService.messageReceived.addListener(self.handleMessageReceived)
		
		# Plugins
		for name, plugin in self.plugins.items():
			self.logger.log("    Enabling plugin \""  + plugin.name + "\"...")
			plugin.initialize(self.logger, self, self.config.plugins.get(name.lower()))
			plugin.enable()
		
		# Start chat services
		for chatServiceName, chatService in self._chatServices.items():
			self.logger.log("Connecting to \"" + chatServiceName + "\"...")
			self._eventLoop.create_task(chatService.connect(self.config.services[chatServiceName]))
		
		try:
			self._eventLoop.run_forever()
		except KeyboardInterrupt:
			for chatServiceName, chatService in self._chatServices.items():
				self.logger.log("Disconnecting from \"" + chatServiceName + "\"...")
				self._eventLoop.run_until_complete(chatService.disconnect())
			
			self.logger.log("Disconnected from all chat services.")
			
			pending = asyncio.Task.all_tasks()
			gathered = asyncio.gather(*pending)
			try: gathered.cancel
			except: pass
		finally:
			self._eventLoop.close()
	
	# Chat Services
	@property
	def chatServices(self):
		return self._chatServices.values()
	
	def getChatService(self, chatServiceName):
		return self._chatServices.get(chatServiceName)
	
	# Plugins
	def addPlugin(self, plugin):
		if isinstance(plugin, type):
			plugin = plugin()
		
		self.plugins[plugin.name] = plugin
		
		if self.running:
			self.logger.log("Enabling plugin \""  + plugin.name + "\"...")
			plugin.initialize(self.logger, self)
			plugin.enable()
	
	def getPlugin(self, name):
		return self.plugins.get(name)
	
	def removePlugin(self, plugin):
		del self.plugins[plugin.name]
		plugin.disable()
		plugin.uninitialize(self.logger, self, self.config.plugins.get(plugin.name.lower()))
	
	# ChatBot
	# Internal
	def handleConnected(self, chatService):
		for server in chatService.servers:
			self.logger.log("Found " + str(server))
			for channel in server.channels:
				self.logger.log("    Found " + str(channel))
		
		# Logging
		for i in range(0, len(self.config.logging.get("destinations", []))):
			loggerConfig = self.config.logging["destinations"][i]
			if loggerConfig["chatService"] != chatService.name: continue
			
			self.channelLoggers[i].channel = chatService.getServerById(loggerConfig["server"]).getChannelByName(loggerConfig["channelName"])
		
		# Check if done
		for chatService in self.chatServices:
			if not chatService.isConnected: return
		
		self.connected(self)
	
	def handleMessageReceived(self, chatService, message):
		try:
			if message.author != message.channel.server.localUser:
				self.commandSystem.handleMessage(message)
			
			self.messageReceived(self, message)
		except (KeyboardInterrupt, SystemExit):
			raise
		except Exception as e:
			self.logger.log(traceback.format_exc())
