from datetime import datetime
import time

from .logger import Logger

class ConsoleLogger(Logger):
	# ILogger
	def logRaw(self, message):
		print(message)
