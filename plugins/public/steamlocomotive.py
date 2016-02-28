import asyncio

from ..base import Plugin

from .steamlocomotiveprocess import SteamLocomotiveProcess

class SteamLocomotive(Plugin):
	def __init__(self):
		super(SteamLocomotive, self).__init__()
	
	# Plugin
	def handleInitialize(self):
		self.registerCommand("sl", self.handleSteamLocomotive).setDescription("list directory contents")
	
	# SteamLocomotive
	# Internal
	def handleSteamLocomotive(self, command, commandInvocation, message):
		SteamLocomotiveProcess(self.logger).start(message.channel)
