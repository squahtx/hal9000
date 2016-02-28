from .commandargument import CommandArgument

class CommandParser(object):
	def __init__(self):
		self.position = 0
		self.text     = None
	
	def parse(self, text):
		self.position = 0
		self.text     = text
		
		arguments = []
		fullArguments = ""
		
		while True:
			self.whitespace()
			
			if len(arguments) == 1:
				fullArguments = self.text[self.position:]
			
			argument = self.argument()
			if argument is None: break
			arguments.append(argument)
		
		commandName = ""
		if len(arguments) > 0:
			commandName = arguments[0].text[1:]
			del arguments[0]
		
		return commandName, arguments, fullArguments
	
	# Internal
	def argument(self):
		# argument          := unquoted-argument | quoted-argument
		# unquoted-argument := ([^ \t"]|\.)+
		# quoted-argument   := "([^"]|\.)*"
		
		if self.isOutOfInput: return None
		
		if self.peek() == '\"':
			return self.quotedArgument()
		
		return self.unquotedArgument()
	
	def unquotedArgument(self):
		# unquoted-argument := ([^ \t"]|\.)+
		
		if self.isOutOfInput: return None
		
		startPosition = self.position
		argument = ""
		
		while not self.isOutOfInput and \
		      not self.peek().isspace():
			if self.peek() == "\"": break
			
			if self.accept("\\"):
				if self.isOutOfInput:
					argument += "\\"
					break
				
				c = self.peek()
				if c in ("\\", "\""): argument += self.acceptAny()
				elif c in (" ", "\r", "\n", "\t"): argument += self.acceptAny()
				elif c == "r": argument += "\r"
				elif c == "n": argument += "\n"
				elif c == "t": argument += "\t"
				else:
					argument += "\\"
					argument += self.acceptAny()
			else:
				argument += self.acceptAny()
		
		return CommandArgument(argument, startPosition, self.position, False)
	
	def quotedArgument(self):
		# quoted-argument := "([^"]|\.)*"
		
		if self.isOutOfInput: return None
		
		# "
		if not self.accept("\""): return None
		
		startPosition = self.position
		argument = ""
		
		while not self.isOutOfInput and \
		      self.peek() != "\"":
			if self.peek() == "\"": break
			
			if self.accept("\\"):
				if self.isOutOfInput:
					argument += "\\"
					break
				
				c = self.peek()
				if c in ("\\", "\""): argument += self.acceptAny()
				elif c in (" ", "\r", "\n", "\t"): argument += self.acceptAny()
				elif c == "r": argument += "\r"
				elif c == "n": argument += "\n"
				elif c == "t": argument += "\t"
				else:
					argument += "\\"
					argument += self.acceptAny()
			else:
				argument += self.acceptAny()
		
		return CommandArgument(argument, startPosition, self.position, True)
	
	def whitespace(self):
		# whitespace := [ \t\r\n]*
		
		# Nom all the whitespace
		while not self.isOutOfInput and \
		      self.text[self.position].isspace():
			self.position += 1
	
	def accept(self, c):
		if self.isOutOfInput: return False
		if self.text[self.position] != c: return False
		
		self.position += 1
		
		return True
	
	def acceptAny(self):
		if self.isOutOfInput: return "\0"
		self.position += 1
		return self.text[self.position - 1]
	
	def peek(self):
		if self.isOutOfInput: return "\0"
		
		return self.text[self.position]
	
	@property
	def isOutOfInput(self):
		return self.position >= len(self.text)
