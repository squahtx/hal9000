from ..base import Plugin

class Help(Plugin):
	# Plugin
	def handleInitialize(self):
		self.registerCommand("help", self.handleHelp).setDescription("Prints out a list of commands.")
		self.registerCommand("f1",   self.handleHelp).setDescription("Prints out a list of commands.")
	
	# Help
	# Internal
	def handleHelp(self, command, commandInvocation, message):
		commandNames = self.chatbot.commandSystem.commands.keys()
		commandNames = sorted(commandNames)
		
		reply = []
		for commandName in commandNames:
			command = self.chatbot.commandSystem.commands[commandName]
			
			line = command.usageString
			if command.description is not None:
				line += " - " + command.description
			
			reply.append(line)
		
		reply = "\n".join(reply)
		
		message.postDelete()
		
		if not message.isPrivateMessage:
			message.channel.postMessage("I have PMed you the list of commands, @" + message.author.displayName + " .")
		
		message.author.postPrivateMessage(reply)
