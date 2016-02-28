from base import abstract

class ILogger(object):
	@abstract
	def log(self, message): pass
	
	@abstract
	def logRaw(self, message): pass
