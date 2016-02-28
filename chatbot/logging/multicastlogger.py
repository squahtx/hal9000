from .logger import Logger

class MulticastLogger(Logger):
	def __init__(self):
		self.loggers = []
	
	# ILogger
	def logRaw(self, message):
		for logger in self.loggers:
			logger.logRaw(message)
	
	# MulticastLogger
	def add(self, logger):
		self.loggers.append(logger)
