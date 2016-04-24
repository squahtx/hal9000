import asyncio

import time

from .logger import Logger

class ChannelLogger(Logger):
	def __init__(self, channel = None):
		super(ChannelLogger, self).__init__()
		
		self._eventLoop           = None
		self._channel             = channel
		
		self.message              = None
		self.messageLength        = 0
		self.maximumMessageLength = 2000 - len("```\n\u200B```")
		
		self.queue                = []
		
		self.dispatchLoopRunning  = False
	
	# ILogger
	def logRaw(self, message):
		self.queue.append(message)
		
		if self.canFlush:
			self.flush()
	
	# ChannelLogger
	@property
	def eventLoop(self):
		return self._eventLoop
	
	@eventLoop.setter
	def eventLoop(self, eventLoop):
		if self._eventLoop == eventLoop: return
		
		self._eventLoop = eventLoop
		
		if self.canFlush:
			self.flush()
	
	@property
	def channel(self):
		return self._channel
	
	@channel.setter
	def channel(self, channel):
		if self._channel == channel: return
		
		self._channel = channel
		self.message = None
		self.messageLength = 0
		
		self.eventLoop = asyncio.get_event_loop()
		
		if self.canFlush:
			self.flush()
	
	@property
	def canFlush(self):
		if self.channel   is None:     return False
		if self.eventLoop is None:     return False
		if self.eventLoop.is_closed(): return False
		
		return True
	
	def flush(self):
		if len(self.queue) == 0: return
		if self.dispatchLoopRunning: return
		
		if not self.canFlush: raise RuntimeError("ChannelLogger.flush : No channel, no event loop or event loop is closed!")
		
		self.dispatchLoopRunning = True
		
		self.eventLoop.create_task(self.dispatchLoop())
	
	@asyncio.coroutine
	def dispatchLoop(self):
		while len(self.queue) > 0:
			remainingLength = self.maximumMessageLength
			
			# Try to reuse message
			reuseMessage = False
			if self.message is not None and \
			   time.time() - self.message.timestamp < 5:
				reuseMessage = True
				remainingLength -= self.messageLength
			
			appendLength = 0
			appendMessages = []
			
			while len(self.queue) > 0:
				requiredLength = 0
				if reuseMessage or len(appendMessages) > 0:
					requiredLength = 1
				
				requiredLength += len(self.queue[0])
				
				# Overflow into next message unless the current message
				if requiredLength > remainingLength:
					if appendLength == 0:
						reuseMessage = False
						remainingLength = self.maximumMessageLength
						
						# Retry
						continue
					else:
						break
				
				remainingLength -= requiredLength
				appendLength += requiredLength
				appendMessages.append(self.queue[0])
				del self.queue[0]
			
			content = "\n".join(appendMessages)
			
			# Try to reuse message
			if reuseMessage:
				self.message = yield from self.dispatchExistingMessage(content)
				self.messageLength += appendLength
			else:
				self.message = yield from self.dispatchNewMessage(content)
				self.messageLength = appendLength
		
		self.dispatchLoopRunning = False
	
	@asyncio.coroutine
	def dispatchExistingMessage(self, message):
		content = self.message.content
		if content.startswith("```"):
			content = content[3:]
		if content.endswith("```"):
			content = content[:-3]
		
		content = content.strip()
		
		content += "\n" + message
		content = "```\n" + content + "```"
		
		return (yield from self.message.editMessage(content))
	
	@asyncio.coroutine
	def dispatchNewMessage(self, message):
		message = "```\n\u200B" + message + "```"
		return (yield from self.channel.sendMessage(message))
