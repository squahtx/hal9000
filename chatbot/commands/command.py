from .commandparameter import CommandParameter

class Command(object):
	def __init__(self, name, handler = None):
		self._name        = name
		self._description = None
		self._handler     = handler
		
		self._helpText    = None
		
		self._parameters  = []
	
	@property
	def name(self):
		return self._name
	
	@property
	def description(self):
		return self._description
	
	@description.setter
	def description(self, description):
		if self._description == description: return
		
		self._description = description
	
	@property
	def helpText(self):
		return self._helpText
	
	@helpText.setter
	def helpText(self, helpText):
		if self._helpText == helpText: return
		
		self._helpText = helpText
	
	@property
	def handler(self):
		return self._handler
	
	@handler.setter
	def handler(self, handler):
		if self._handler == handler: return
		
		self._handler = handler
	
	@property
	def parameterCount(self):
		return len(self._parameters)
	
	@property
	def parameters(self):
		return self._parameters
	
	def addParameter(self, name):
		parameter = CommandParameter(name)
		self.parameters.append(parameter)
		return self
	
	def setDescription(self, description):
		self.description = description
		return self
	
	def setHelpText(self, helpText):
		self.helpText = helpText
		return self
	
	def setHandler(self, handler):
		self.handler = handler
		return self
	
	@property
	def usageString(self):
		usageString = "!" + self.name
		
		parameters = ["<" + parameter.name + ">" for parameter in self.parameters]
		parameters = " ".join(parameters)
		
		if len(parameters) > 0:
			usageString += " " + parameters
		
		return usageString
	
	def handle(self, message, commandInvocation):
		if commandInvocation.argumentCount < self.parameterCount:
			self.printUsage(message.channel)
			return
		
		return self.handler(self, commandInvocation, message)
	
	# Internal
	def printUsage(self, chatChannel):
		if self.helpText is not None:
			chatChannel.postMessage(self.usageString + "\n" + self.helpText)
		else:
			chatChannel.postMessage(self.usageString)
