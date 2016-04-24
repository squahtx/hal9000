import asyncio
import atexit
import fcntl
import os
import pty
import select
import struct
import subprocess
import termios
import threading
import time

from base import Event

from .terminalemulator import TerminalEmulator

class TerminalEmulatedProcess(object):
	def __init__(self):
		super(TerminalEmulatedProcess, self).__init__()
		
		self._terminated    = Event("terminated")
		self._screenUpdated = Event("screenUpdated")
		
		self._logger = None
		
		self._terminalEmulator = TerminalEmulator()
		self._terminalEmulator.resize(80, 24)
		
		self.masterPty    = None
		self.slavePty     = None
		self.process      = None
		
		self.outputThread = None
	
	# Events
	@property
	def terminated(self):
		return self._terminated
	
	@property
	def screenUpdated(self):
		return self._screenUpdated
	
	# Logging
	@property
	def logger(self):
		return self._logger
	
	@logger.setter
	def logger(self, logger):
		if self._logger == logger: return
		
		self._logger = logger
		self.terminalEmulator.logger = self._logger
	
	# Process
	@property
	def terminalEmulator(self):
		return self._terminalEmulator
	
	@property
	def running(self):
		return self.process is not None
	
	def start(self, commandLine, **kwargs):
		if self.process is not None:
			raise RuntimeError()
		
		atexit.register(self.terminate)
		
		self.terminalEmulator.reset()
		
		self.masterPty, self.slaveTty = pty.openpty()
		
		fcntl.ioctl(self.masterPty, termios.TIOCSWINSZ, struct.pack("HHHH", self.terminalEmulator.height, self.terminalEmulator.width, 0, 0))
		
		self.process = subprocess.Popen(commandLine, stdin = self.slaveTty, stdout = self.slaveTty, **kwargs)
		
		self.outputThread = threading.Thread(target = self.runOutputThread)
		self.outputThread.daemon = True
		self.outputThread.start()
	
	def terminate(self):
		if self.masterPty is None and \
		   self.slavePty is None and \
		   self.process is None:
			return
		
		try: os.close(self.masterPty)
		except (TypeError, OSError): pass
		
		try: os.close(self.slaveTty)
		except (TypeError, OSError): pass
		
		if self.process is not None: self.process.kill()
		
		self.masterPty = None
		self.slaveTty  = None
		self.process   = None
		
		atexit.unregister(self.terminate)
		
		self.terminated(self)
	
	# Input
	def write(self, text):
		os.write(self.masterPty, text)
	
	# Output
	def runOutputThread(self):
		poll = select.poll()
		poll.register(self.masterPty)
		while self.process is not None:
			events = poll.poll(0)
			if len(events) > 0 and events[0][1] & select.POLLIN == select.POLLIN:
				c = os.read(self.masterPty, 1024)
				if c is None or c == b'': break
				self.terminalEmulator.write(c)
				self.screenUpdated(self, self.terminalEmulator)
			elif self.process.poll() is not None:
				break
			else:
				time.sleep(0.1)
		
		poll.unregister(self.masterPty)
		
		self.outputThread = None
		
		self.process.wait()
		self.process = None
		
		self.terminate()
