import asyncio

import time

from .logger import Logger

class ChannelLogger(Logger):
	def __init__(self, channel = None):
		super(ChannelLogger, self).__init__()
		
		self._eventLoop          = None
		self._channel            = channel
		
		self.message             = None
		self.messageLineCount    = 0
		self.linesPerMessage     = 20
		
		self.queue               = []
		
		self.dispatchLoopRunning = False
	
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
		self.messageLineCount = 0
		
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
			lineCount = self.linesPerMessage - self.messageLineCount
			lines = self.queue[0:lineCount]
			content = "\n".join(lines)
			self.queue = self.queue[lineCount:]
			lineCount = len(lines)
			
			if self.message is not None and \
			   time.time() - self.message.timestamp < 5:
				self.message = yield from self.dispatchExistingMessage(content)
				self.messageLineCount + lineCount
			else:
				self.message = yield from self.dispatchNewMessage(content)
				self.messageLineCount = lineCount
			
			if self.messageLineCount >= self.linesPerMessage:
				self.message = None
				self.messageLineCount = 0
		
		self.dispatchLoopRunning = False
	
	@asyncio.coroutine
	def dispatchExistingMessage(self, message):
		content = self.message.content
		if content.startswith("```"):
			content = content[3:]
		if content.endswith("```"):
			content = content[:-3]
		
		content = content.strip()
		
		content += "\r\n" + message
		content = "```\n" + content + "```"
		
		return (yield from self.message.editMessage(content))
	
	@asyncio.coroutine
	def dispatchNewMessage(self, message):
		message = "```\n\u200B" + message + "```"
		return (yield from self.channel.sendMessage(message))
