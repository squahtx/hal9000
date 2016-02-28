import re

from ..base import Plugin

class PodBayDoors(Plugin):
	# Plugin
	def handleEnabled(self):
		self.chatbot.messageReceived.addListener("PodBayDoors", self.handleMessageReceived)
	
	def handleDisabled(self):
		self.chatbot.messageReceived.removeListener("PodBayDoors")
	
	# PodBayDoors
	# Internal
	def handleMessageReceived(self, chatbot, message):
		text = message.content
		text = text.lower()
		text = re.sub(r"[^a-zA-Z0-9]+", u"", text)
		if text == "openthepodbaydoors" or \
		   text == "openthepodbaydoorshal":
			chatbot.logger.log("PodBayDoors.handleMessageReceived : Refusing to open pod bay doors for " + message.author.displayName + ".")
			message.channel.postMessage("I'm sorry @" + message.author.displayName + ", I'm afraid I can't do that.")
