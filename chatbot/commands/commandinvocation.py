from .commandparser import CommandParser

class CommandInvocation(object):
	def __init__(self, message):
		self._message = message
		
		self._fullCommand = message.content
		
		name, arguments, fullArguments = CommandParser().parse(self.fullCommand)
		self._name = name
		self._arguments = arguments
		self._fullArguments = fullArguments
	
	@property
	def message(self):
		return self._message
	
	@property
	def fullCommand(self):
		return self._fullCommand
	
	@fullCommand.setter
	def fullCommand(self, fullCommand):
		self._fullCommand = fullCommand
	
	@property
	def fullArguments(self):
		return self._fullArguments
	
	@fullArguments.setter
	def fullArguments(self, fullArguments):
		self._fullArguments = fullArguments
	
	@property
	def name(self):
		return self._name
	
	@name.setter
	def name(self, name):
		self._name = name
	
	@property
	def arguments(self):
		return self._arguments
	
	@property
	def argumentCount(self):
		return len(self.arguments)
	
	def remainingArguments(self, n):
		if n >= len(self.arguments): return ""
		return self.fullCommand[self.arguments[n].startPosition:]
