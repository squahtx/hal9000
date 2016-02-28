from .commandinvocation import CommandInvocation

class CommandSystem(object):
	def __init__(self, logger):
		super(CommandSystem, self).__init__()
		
		self.logger            = logger
		
		self.commands          = {}
		self.lowercaseCommands = {}
	
	def registerCommand(self, name, command):
		self.commands[name] = command
		self.lowercaseCommands[name.lower()] = command
	
	def unregisterCommand(self, name):
		command = self.commands[name]
		del self.commands[name]
		if self.lowercaseCommands[name.lower()] == command:
			del self.lowercaseCommands[name.lower()]
	
	def handleMessage(self, message):
		if len(message.content) == 0: return False
		if message.content[0] not in ("!", "/"): return False
		
		commandInvocation = CommandInvocation(message)
		
		command = None
		if commandInvocation.name in self.commands:
			command = self.commands[commandInvocation.name]
		elif commandInvocation.name.lower() in self.lowercaseCommands:
			command = self.lowercaseCommands[commandInvocation.name.lower()]
		
		if command is None: return False
		
		self.logger.log("Channel " + message.channel.globalId + ": " + message.author.displayName + " ran command " + commandInvocation.fullCommand)
		
		command.handle(message, commandInvocation)
		
		return True
