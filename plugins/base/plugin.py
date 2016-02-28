import os.path

from .iplugin import IPlugin

from chatbot.commands import Command

class Plugin(IPlugin):
	def __init__(self):
		self._logger  = None
		self._chatbot = None
		self._config  = None
		
		self._enabled = False
		
		self._commands = {}
		
		self.userData    = {}
		self.channelData = {}
	
	# IPlugin
	@property
	def name(self):
		return self.__class__.__name__
	
	def initialize(self, logger, chatbot, config):
		if config is None: config = {}
		
		self._logger  = logger
		self._chatbot = chatbot
		self._config  = config
		
		self.handleInitialize()
	
	def uninitialize(self, logger, chatbot, config):
		self.handleUninitialize()
		
		self._logger  = None
		self._chatbot = None
		self._config  = None
	
	@property
	def enabled(self):
		return self._enabled
	
	@enabled.setter
	def enabled(self, enabled):
		if self._enabled == enabled: return
		
		self._enabled = enabled
		if self._enabled:
			for name, command in self.commands.items():
				self.chatbot.commandSystem.registerCommand(name, command)
			
			self.handleEnabled()
		else:
			self.handleDisabled()
			
			for name in self.commands.keys():
				self.chatbot.commandSystem.unregisterCommand(name)
	
	def enable(self):
		self.enabled = True
	
	def disable(self):
		self.enabled = False
	
	# Plugin
	# Internal
	@property
	def chatbot(self):
		return self._chatbot
	
	# Logging
	@property
	def logger(self):
		return self._logger
	
	def log(self, message):
		if self.logger is None: return
		
		self.logger.log("[" + self.name + "] " + message)
	
	# Configuration
	@property
	def config(self):
		return self._config
	
	# Data
	@property
	def dataDirectory(self):
		path = os.path.join(__file__, "../../data")
		path = os.path.join(path, self.name.lower())
		path = os.path.normpath(path)
		
		if not os.path.exists(path):
			os.makedirs(path)
			self.log("Created data directory.")
		
		return path
	
	def getTemporaryUserData(self, user):
		globalId = user.globalId
		if globalId not in self.userData:
			self.userData[globalId] = {}
			self.handleInitializeTemporaryUserData(user, self.userData[globalId])
		
		return self.userData[globalId]
	
	def getTemporaryChannelData(self, channel):
		globalId = channel.globalId
		if globalId not in self.channelData:
			self.channelData[globalId] = {}
			self.handleInitializeTemporaryChannelData(channel, self.channelData[globalId])
		
		return self.channelData[globalId]
	
	# State
	def handleInitialize(self): pass
	def handleUninitialize(self): pass
	
	def handleEnabled(self): pass
	def handleDisabled(self): pass
	
	def handleInitializeTemporaryUserData(self, user, userData): pass
	def handleInitializeTemporaryChannelData(self, channel, channelData): pass
	
	# Commands
	@property
	def commands(self):
		return self._commands
	
	def registerCommand(self, name, commandHandler):
		command = Command(name, commandHandler)
		self.commands[name] = command
		
		if self.chatbot is not None and self.enabled:
			self.chatbot.commandSystem.registerCommand(name, command)
		
		return command
	
	def unregisterCommand(self, name):
		self.commands[name] = name
		
		if self.chatbot is not None:
			self.chatbot.commandSystem.unregisterCommand(name)
