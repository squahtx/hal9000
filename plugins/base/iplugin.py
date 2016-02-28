from base import abstract

class IPlugin(object):
	@property
	@abstract
	def name(self): pass

	@abstract
	def initialize(self, logger, chatbot): pass
	
	@abstract
	def uninitialize(self, logger, chatbot): pass
	
	@property
	@abstract
	def enabled(self): pass
	
	@enabled.setter
	@abstract
	def enabled(self, enabled): pass
	
	@abstract
	def enable(self): pass
	
	@abstract
	def disable(self): pass
