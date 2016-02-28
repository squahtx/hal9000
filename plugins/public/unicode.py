import re
import unicodedata

from ..base import Plugin

class Unicode(Plugin):
	# Plugin
	def handleInitialize(self):
		self.registerCommand("unicode", self.handleUnicodeSearch).setDescription("Searches for Unicode code points by name.").addParameter("search text")
		self.registerCommand("utf8",    self.handleUnicodeSearch).setDescription("Searches for Unicode code points by name.").addParameter("search text")
		self.registerCommand("utf16",   self.handleUnicodeSearch).setDescription("Searches for Unicode code points by name.").addParameter("search text")
	
	def handleEnabled(self):
		self.chatbot.messageReceived.addListener("Unicode", self.handleMessageReceived)
	
	def handleDisabled(self):
		self.chatbot.messageReceived.removeListener("Unicode")
	
	# Unicode
	# Internal
	def handleMessageReceived(self, chatbot, message):
		text = message.content
		if not text.startswith("u\""): return
		
		self.dissectUnicode(message, text)
	
	def handleUnicodeSearch(self, command, commandInvocation, message):
		searchText = commandInvocation.fullArguments
		searchText = searchText.strip()
		lowercaseSearchText = searchText.lower()
		
		if len(lowercaseSearchText) == 0:
			message.channel.postMessage("You must provide a search term!")
			return
		
		results = []
		aborted = False
		for i in range(0, 0x110000):
			c = chr(i)
			name = unicodedata.name(c, "").lower()
			if lowercaseSearchText in name:
				if len(results) >= 5:
					aborted = True
					break
				else:
					results.append(self.formatCharacterInformation(c))
		
		if len(results) == 0:
			if self.containsInterestingUtf8(searchText):
				self.dissectUnicode(message, text)
			else:
				message.channel.postMessage("No matching code points found :(")
		else:
			if aborted: results.append("...")
			reply = "\n".join(results)
			reply = "```\n" + reply + "```"
			
			message.channel.postMessage(reply)
	
	def dissectUnicode(self, message, text, showUtf8 = None, showUtf16 = None):
		try:
			text = self.interpretInput(text)
		except UnicodeDecodeError:
			message.channel.postMessage("Invalid utf-8!")
			return
		
		# Truncate
		truncated = False
		if len(text) > 5:
			text = text[0:5]
			truncated = True
		
		content = ""
		if showUtf8 or (showUtf8 is None and self.containsInterestingUtf8(text)):
			content += "UTF-8: \"" + self.escapeUtf8(text) + ("..." if truncated else "") + "\"\n"
		if showUtf16 or (showUtf16 is None and self.containsInterestingUtf16(text)):
			content += "UTF-16LE: \"" + self.escapeUtf16LE(text) + ("..." if truncated else "") + "\"\n"
		
		lines = []
		for c in text:
			lines.append(self.formatCharacterInformation(c))
		if truncated: lines.append("...")
		
		content += "\n".join(lines)
		content = "```\n" + content + "```"
		message.channel.postMessage(content)
	
	def formatCharacterInformation(self, c):
		codePoint = ord(c)
		printableCharacter = c
		if unicodedata.category(c) in ("Zs", "Zl", "Zp", "Cc", "Cf", "Cs", "Co", "Cn"):
			printableCharacter = " "
		name = unicodedata.name(c, "")
		
		return "U+%06X %s %s" % (codePoint, printableCharacter, name)
	
	def escapeUtf8(self, str):
		bytes = str.encode("utf-8")
		return self.escapeBytes(bytes)
		escapedString = ""
		for uint8 in bytes:
			if 0x20 <= uint8 and uint8 < 0x7F:
				escapedString += chr(uint8)
			else:
				escapedString += "\\x%02x" % uint8
		return escapedString
	
	def escapeUtf16LE(self, str):
		bytes = str.encode("utf-16le")[2:]
		return self.escapeBytes(bytes)
	
	def escapeUtf16BE(self, str):
		bytes = str.encode("utf-16be")[2:]
		return self.escapeBytes(bytes)
	
	def escapeBytes(self, bytes):
		escapedString = ""
		for uint8 in bytes:
			if 0x20 <= uint8 and uint8 < 0x7F:
				escapedString += chr(uint8)
			else:
				escapedString += "\\x%02x" % uint8
		return escapedString
	
	def unescape(self, str):
		bytes = bytearray()
		i = 0
		while i < len(str):
			c = str[i]
			i += 1
			
			if c == "\\":
				if i >= len(str):
					bytes.extend(b"\\")
					break
				
				c = str[i]
				i += 1
				
				if c == "\\":   bytes.extend(b"\\")
				elif c == "\r": bytes.extend(b"\r")
				elif c == "\n": bytes.extend(b"\n")
				elif c == "\t": bytes.extend(b"\t")
				elif c == "x":
					n = str[i:i + 2]
					i += 2
					try:
						n = int(n, 16)
						bytes.append(n)
					except ValueError:
						bytes.extend(b"\\x")
						bytes.extend(n)
				elif c == "u":
					n = str[i:i + 4]
					i += 4
					try:
						n = int(n, 16)
						bytes.extend(chr(n).encode("utf-8"))
					except ValueError:
						bytes.extend(b"\\u")
						bytes.extend(n)
				elif c == "U":
					n = str[i:i + 6]
					i += 6
					try:
						n = int(n, 16)
						bytes.extend(chr(n).encode("utf-8"))
					except ValueError:
						bytes.extend(b"\\U")
						bytes.extend(n)
				else:
					bytes.extend(b"\\")
					bytes.extend(c.encode("utf-8"))
			else:
				bytes.extend(c.encode("utf-8"))
		
		return bytes.decode("utf-8")
	
	def containsInterestingUtf8(self, str):
		for c in str:
			if ord(c) >= 0x80: return True
		return False
	
	def containsInterestingUtf16(self, str):
		for c in str:
			if ord(c) >= 0x010000: return True
		return False
	
	def interpretInput(self, str):
		if str.startswith("u\""):
			str = str[2:-1] if str.endswith("\"") else str[2:]
			str = self.unescape(str)
		elif str.startswith("\""):
			str = str[1:-1] if str.endswith("\"") else str[1:]
			str = self.unescape(str)
		
		return str
