class CommandArgument(object):
	def __init__(self, text, startPosition, endPosition, quoted):
		self._text = text
		self._startPosition = startPosition
		self._endPosition = endPosition
		self._quoted = quoted
	
	@property
	def text(self):
		return self._text
	
	@property
	def startPosition(self):
		return self._startPosition
	
	@property
	def endPosition(self):
		return self._endPosition
	
	@property
	def isQuoted(self):
		return self._quoted
