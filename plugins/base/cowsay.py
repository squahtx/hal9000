import os.path
import subprocess

from .plugin import Plugin

class CowSay(Plugin):
	# CowSay
	# Internal
	def handleSay(self, command, commandInvocation, message, text, animal):
		output = None
		try:
			output = subprocess.check_output(["cowsay", "-f", animal], input = text.encode("utf-8"))
		except:
			output = b""
		
		output = output.decode("utf-8")
		output = output.rstrip()
		output = "```\n\u200B" + output + "```"
		
		message.channel.postMessage(output)
