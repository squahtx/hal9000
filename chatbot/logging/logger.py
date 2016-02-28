from datetime import datetime
import time

from base import abstract

from .ilogger import ILogger

class Logger(ILogger):
	# ILogger
	def log(self, message):
		timestamp = time.time()
		
		date = datetime.utcfromtimestamp(timestamp)
		timeString = date.strftime("%Y-%m-%d %H:%M:%S.%f UTC+0000")
		
		message = "[" + timeString + "] " + message
		
		self.logRaw(message)
