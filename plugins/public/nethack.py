import asyncio
import atexit
import traceback

from ..base import Plugin

from ..base import TerminalEmulatedProcess

class NetHack(Plugin):
	def __init__(self):
		super(NetHack, self).__init__()
		
		self.eventLoop                   = None
		
		self.updateLoopRunning           = False
		
		self._channel                    = None
		self.channelInitialized          = False
		self.message                     = None
		self.commandHistoryMessage       = None
		
		self.pendingScreenUpdate         = False
		self.pendingMessageDeletions     = []
		self.pendingCommandHistoryUpdate = False
		
		self.commandHistory              = [""] * 5
		
		self.terminalEmulatedProcess     = TerminalEmulatedProcess()
		self.terminalEmulatedProcess.terminalEmulator.resize(80, 24)
		self.terminalEmulatedProcess.screenUpdated.addListener(self.handleScreenUpdate)
		self.terminalEmulatedProcess.terminated.addListener(self.handleTerminated)
		self.autoRestart                 = True
		
		self.composableKeyMap = {}
		self.keyMap = {}
		
		self.composableKeyMap["^c"] = "\x03"
		self.composableKeyMap["^p"] = "\x10"
		self.composableKeyMap["\\n"] = "\n"
		self.composableKeyMap["\\x1b"] = "\x1b"
		self.composableKeyMap["^["] = "\x1b"
		
		self.keyMap["^c"] = "\x03"
		self.keyMap["^p"] = "\x10"
		self.keyMap["\\n"] = "\n"
		self.keyMap["\\x1b"] = "\x1b"
		self.keyMap["^["] = "\x1b"
		
		self.keyMap["enter"] = "\n"
		self.keyMap["esc"] = "\x1b"
		self.keyMap["escape"] = "\x1b"
		self.keyMap["up"] = "8"
		self.keyMap["down"] = "2"
		self.keyMap["left"] = "4"
		self.keyMap["right"] = "6"
		self.keyMap["ascend"] = "<"
		self.keyMap["descend"] = ">"
		self.keyMap["help"] = ""
	
	# Plugin
	def handleInitialize(self):
		self.eventLoop = asyncio.get_event_loop()
		
		self.createProcess()
		
		self.handleConnected(self.chatbot)
		self.addChatBotListeners(self.chatbot)
		
		self.registerCommand("nh", self.handleNetHack).setDescription("Send NetHack keyboard input.")
		self.registerCommand("nethack", self.handleNetHack).setDescription("Send NetHack keyboard input.")
	
	def handleUninitialize(self):
		self.removeChatBotListeners(self.chatbot)
		
		self.channel = None
		
		self.terminateProcess()
		
		self.eventLoop = None
	
	# NetHack
	# Internal
	def handleNetHack(self, command, commandInvocation, message):
		self.handleInput(message.author, commandInvocation.fullArguments)
	
	# Process
	def createProcess(self):
		if self.terminalEmulatedProcess.running: return
		self.log("Starting nethack...")
		
		self.autoRestart = True
		
		self.terminalEmulatedProcess.logger = self.logger
		self.terminalEmulatedProcess.start(["nethack"])
		
		atexit.register(self.terminateProcess)
	
	def terminateProcess(self):
		self.log("Terminating nethack...")
		
		self.autoRestart = False
		
		self.terminalEmulatedProcess.terminate()
		self.terminalEmulatedProcess.logger = None
		
		atexit.unregister(self.terminateProcess)
	
	# Output
	def handleScreenUpdate(self, terminalEmulatedProcess, terminalEmulator):
		self.queueScreenUpdate()
	
	def handleTerminated(self, terminalEmulatedProcess):
		self.queueScreenUpdate()
		
		# Restart NetHack if the termination was not scheduled
		if self.autoRestart:
			self.log("Unscheduled termination, restarting nethack...")
			self.terminateProcess()
			self.createProcess()
	
	# Chat bot
	def addChatBotListeners(self, chatbot):
		if chatbot is None: return
		
		chatbot.connected.addListener(self.name, self.handleConnected)
	
	def removeChatBotListeners(self, chatbot):
		if chatbot is None: return
		
		chatbot.connected.removeListener(self.name)
	
	def handleConnected(self, chatbot):
		chatService = chatbot.getChatService(self.config.get("chatService"))
		server      = None
		channel     = None
		if chatService is not None: server  = chatService.getServerById(self.config.get("server"))
		if server      is not None: channel = server.getChannelByName(self.config.get("channelName"))
		
		self.channel = channel
		
		if self.channel is None:
			self.log("No channel provided in config or failed to find channel.")
	
	# Channel
	@property
	def channel(self):
		return self._channel
	
	@channel.setter
	def channel(self, channel):
		if self._channel == channel: return
		
		self.removeChannelListeners(self._channel)
		self._channel = channel
		self.addChannelListeners(self._channel)
		
		if self._channel is not None:
			self.log("Attached to " + str(self._channel))
		
		self.channelInitialized    = False
		self.message               = None
		self.commandHistoryMessage = None
		
		self.queueScreenUpdate()
		self.queueCommandHistoryUpdate()
	
	@asyncio.coroutine
	def clearChannel(self):
		self.log("Clearing channel...")
		
		# HACK: Delete Discord messages
		if getattr(self.channel.chatService.client, "logs_from", None):
			from chat.discord import DiscordMessage
			
			messages = yield from self.channel.chatService.client.logs_from(self.channel.channel)
			for message in messages:
				yield from DiscordMessage(self.channel.chatService, message).delete()
	
	def addChannelListeners(self, channel):
		if channel is None: return
		
		channel.messageReceived.addListener(self.name, self.handleMessageReceived)
	
	def removeChannelListeners(self, channel):
		if channel is None: return
		
		channel.messageReceived.removeListener(self.name)
	
	def handleMessageReceived(self, chatService, channel, message):
		if message.author == message.server.localUser: return
		
		self.handleInput(message.author, message.content)
		
		message.postDelete()
	
	def handleInput(self, user, content):
		if self.terminalEmulatedProcess.running:
			input = content
			if input.lower() in self.keyMap:
				input = self.keyMap[input.lower()]
			
			for k, v in self.composableKeyMap.items():
				input = input.replace(k, v)
			
			self.terminalEmulatedProcess.write(input.encode("utf-8"))
		
		del self.commandHistory[0]
		self.commandHistory.append("@\u200B" + user.displayName + ": " + content)
		self.queueCommandHistoryUpdate()
	
	# Output
	def startUpdateLoop(self):
		if self.updateLoopRunning:     return
		if self.channel is None:       return
		if self.eventLoop.is_closed(): return
		
		self.updateLoopRunning = True
		
		self.eventLoop.create_task(self.updateLoop())
	
	def stopUpdateLoop(self):
		self.updateLoopRunning = False
	
	def queueScreenUpdate(self):
		self.pendingScreenUpdate = True
		
		if self.updateLoopRunning: return
		self.startUpdateLoop()
	
	def queueMessageDeletion(self, message):
		self.pendingMessageDeletions.append(message)
		
		if self.updateLoopRunning: return
		self.startUpdateLoop()
	
	def queueCommandHistoryUpdate(self):
		self.pendingCommandHistoryUpdate = True
		
		if self.updateLoopRunning: return
		self.startUpdateLoop()
	
	def formatHelpAndCommandHistoryMessage(self):
		message = "```\n" \
		          "Controls: [789456123]movement [esc(ape)] [\\n]enter                | [W]ear [R]emove [T]ake-off [P]ut-on\n" \
		          "          [q]uaff [w]ield     [e]at      [i]nventory [o]pen [p]ay | [Z]cast\n" \
		          "          [a]pply [s]earch    [d]rop     [k]ick                   | [#loot] [#pray] [#chat]\n" \
		          "          [z]ap   [,]pick-up  [.]wait    [<, >]stairs             | \n"
		message += "\n".join(self.commandHistory)
		
		# HACK: Slack does not allow message deletion
		from chat.slack import SlackChatService
		if isinstance(self.channel.chatService, SlackChatService):
			message += "\nPlease use the !nh command in a private message to the bot to submit keyboard input."
		
		message += "\u200B```"
		return message
	
	@asyncio.coroutine
	def updateLoop(self):
		if not self.channelInitialized:
			yield from self.clearChannel()
			self.channelInitialized = True
			self.message = yield from self.channel.sendMessage("```\n\u200B" + self.terminalEmulatedProcess.terminalEmulator.buffer + "\u200B```")
			self.commandHistoryMessage = yield from self.channel.sendMessage("```\n```")
		
		while self.channel is not None:
			if not self.pendingScreenUpdate and \
			   not self.pendingCommandHistoryUpdate and \
			   len(self.pendingMessageDeletions) == 0:
				break
			
			if self.pendingScreenUpdate:
				self.pendingScreenUpdate = False
				
				screenBuffer = self.terminalEmulatedProcess.terminalEmulator.buffer
				try:
					yield from self.message.editMessage("```\n\u200B" + screenBuffer + "\u200B```")
				except:
					self.logger.log(traceback.format_exc())
					self.pendingScreenUpdate = True
			
			if self.pendingCommandHistoryUpdate:
				self.pendingCommandHistoryUpdate = False
				
				try:
					yield from self.commandHistoryMessage.editMessage(self.formatHelpAndCommandHistoryMessage())
				except:
					self.logger.log(traceback.format_exc())
					self.pendingCommandHistoryUpdate = True
			
			if len(self.pendingMessageDeletions) > 0:
				pendingMessageDeletions = self.pendingMessageDeletions
				self.pendingMessageDeletions = []
				
				for message in pendingMessageDeletions:
					try:
						yield from message.delete()
					except:
						self.logger.log(traceback.format_exc())
						self.pendingMessageDeletions.append(message)
		
		self.updateLoopRunning = False
