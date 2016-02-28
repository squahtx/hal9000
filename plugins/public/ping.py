from ..base import Plugin

class Ping(Plugin):
	# Plugin
	def handleInitialize(self):
		self.registerCommand("ping", self.handlePing).setDescription("Test the bot for up-ness.")
	
	# Ping
	# Internal
	def handlePing(self, command, commandInvocation, message):
		message.channel.postMessage("ICMP ECHO REPLY.")
