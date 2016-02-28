import asyncio
import atexit
import traceback

from ..base import Plugin

from ..base import TerminalEmulatedProcess

class SteamLocomotiveProcess(object):
	def __init__(self, logger):
		super(SteamLocomotiveProcess, self).__init__()
		
		self.logger                      = logger
		
		self.eventLoop                   = None
		
		self.channel                     = None
		
		self.updateLoopRunning           = False
		
		self.terminalEmulatedProcess     = TerminalEmulatedProcess()
		self.terminalEmulatedProcess.terminalEmulator.resize(80, 24)
		self.terminalEmulatedProcess.screenUpdated.addListener(self.handleScreenUpdate)
		self.terminalEmulatedProcess.terminated.addListener(self.handleTerminated)
		
		self.message                     = None
		
		self.pendingScreenUpdate         = False
	
	def start(self, channel, eventLoop = None):
		if eventLoop is None: eventLoop = asyncio.get_event_loop()
		self.eventLoop = eventLoop
		
		self.channel = channel
		
		self.terminalEmulatedProcess.logger = self.logger
		
		self.terminalEmulatedProcess.terminate()
		self.terminalEmulatedProcess.start(["sl"])
		
		self.queueScreenUpdate()
	
	@asyncio.coroutine
	def run(self, channel):
		if self.message is None:
			self.message = yield from self.channel.sendMessage("")
	
	# Output
	def handleScreenUpdate(self, terminalEmulatedProcess, terminalEmulator):
		self.queueScreenUpdate()
	
	def handleTerminated(self, terminalEmulatedProcess):
		self.queueScreenUpdate()
	
	def startUpdateLoop(self):
		if self.updateLoopRunning:     return
		if self.channel is None:       return
		if self.eventLoop.is_closed(): return
		
		self.updateLoopRunning = True
		
		self.eventLoop.create_task(self.updateLoop())
	
	def stopUpdateLoop(self):
		self.updateLoopRunning = False
	
	def queueScreenUpdate(self):
		self.pendingScreenUpdate = True
		
		if self.updateLoopRunning: return
		self.startUpdateLoop()
	
	@asyncio.coroutine
	def updateLoop(self):
		if not self.message:
			self.message = yield from self.channel.sendMessage("```\n\u200B" + self.terminalEmulatedProcess.terminalEmulator.buffer + "\u200B```")
		
		while self.channel is not None:
			if not self.pendingScreenUpdate:
				break
			
			self.pendingScreenUpdate = False
			
			screenBuffer = self.terminalEmulatedProcess.terminalEmulator.buffer
			try:
				yield from self.message.editMessage("```\n\u200B" + screenBuffer + "\u200B```")
			except:
				self.logger.log(traceback.format_exc())
				self.pendingScreenUpdate = True
		
		if not self.terminalEmulatedProcess.running:
			self.message.postDelete()
		
		self.updateLoopRunning = False
