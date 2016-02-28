from ..base import CowSay

class CowSay(CowSay):
	# Plugin
	def handleInitialize(self):
		super(CowSay, self).handleInitialize()
		
		self.registerCommand("cowsay",    self.handleCowSay).setDescription("Moo.")
		self.registerCommand("dinosay",   self.handleDinosaurSay).setDescription("Rawr.")
		self.registerCommand("dragonsay", self.handleDragonSay).setDescription("Rawr.")
		self.registerCommand("mechsay",   self.handleMechSay).setDescription("BEEP BOOP.")
		self.registerCommand("ponysay",   self.handlePonySay).setDescription("Friendship is magic.")
		
		for _, command in self.commands.items():
			command.addParameter("message")
	
	# CowSay
	# Internal
	def handleCowSay(self, command, commandInvocation, message):
		self.handleSay(command, commandInvocation, message, commandInvocation.fullArguments, "default")
	
	def handleDinosaurSay(self, command, commandInvocation, message):
		self.handleSay(command, commandInvocation, message, commandInvocation.fullArguments, "stegosaurus")
	
	def handleDragonSay(self, command, commandInvocation, message):
		self.handleSay(command, commandInvocation, message, commandInvocation.fullArguments, "dragon-and-cow")
	
	def handleMechSay(self, command, commandInvocation, message):
		self.handleSay(command, commandInvocation, message, commandInvocation.fullArguments.upper(), "mech-and-cow")
	
	def handlePonySay(self, command, commandInvocation, message):
		self.handleSay(command, commandInvocation, message, commandInvocation.fullArguments, "unipony-smaller")
