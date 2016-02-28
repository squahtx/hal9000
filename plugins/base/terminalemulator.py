import asyncio

from base import Event

class TerminalEmulator(object):
	def __init__(self):
		super(TerminalEmulator, self).__init__()
		
		self._logger        = None
		
		self.revision       = 0
		self._width         = 0
		self._height        = 0
		self.lines          = []

		self.cursorX        = 0
		self.cursorY        = 0
		
		self.coroutine      = None
		self.peekBuffer     = None
		
		self.resize(80, 24)
	
	# TerminalEmulator
	@property
	def logger(self):
		return self._logger
	
	@logger.setter
	def logger(self, logger):
		self._logger = logger
	
	@property
	def width(self):
		return self._width
	
	@property
	def height(self):
		return self._height
	
	@width.setter
	def width(self, width):
		self.resize(width, self.height)
	
	@height.setter
	def height(self, height):
		self.resize(self.width, height)
	
	def clear(self):
		for y in range(0, self.height):
			self.lines[y] = [" "] * self.width
	
	def reset(self):
		self.clear()
		self.cursorX = 0
		self.cursorY = 0
	
	def resize(self, w, h):
		if self._width != w:
			self.lines = [line[0:w] for line in self.lines]
			
			for y in range(0, self._height):
				line = self.lines[y]
				while len(line) < w:
					line.append(" ")
			
			self._width = w
		
		if self._height != h:
			self.lines = self.lines[0:h]
			
			while h > len(self.lines):
				self.lines.append([" "] * self._width)
			
			self._height = h
		
		self.clampCursor()
	
	@property
	def buffer(self):
		return "\n".join([self.bufferLine(y) for y in range(0, self.height)])
	
	def bufferLineRange(self, startLine, endLine):
		return "\n".join([self.bufferLine(y) for y in range(startLine, endLine)])
	
	def bufferLine(self, line):
		if line != self.cursorY: return "".join(self.lines[line]).rstrip()
		return "".join(self.lines[line][0:self.cursorX]) + "\u200B\u0332" + "".join(self.lines[line][(self.cursorX):])
	
	def write(self, bytes):
		if self.coroutine is None:
			self.coroutine = self.processInput()
			next(self.coroutine)
		
		for b in bytes:
			self.coroutine.send(b)
	
	# Internal
	def clampCursor(self):
		self.cursorX = max(0, min(self.cursorX, self.width - 1))
		self.cursorY = max(0, min(self.cursorY, self.height - 1))
	
	def setCursorPos(self, x, y):
		self.cursorX = x
		self.cursorY = y
		
		self.clampCursor()
	
	@asyncio.coroutine
	def processInput(self):
		while True:
			c = yield from self.readCharacter()
			
			if c == "\x08":
				if self.cursorX == 0:
					if self.cursorY > 0:
						self.setCursorPos(self.width - 1, self.cursorY - 1)
					else:
						pass
				else:
					self.setCursorPos(self.cursorX - 1, self.cursorY)
			elif c == "\r":
				self.processCarriageReturn()
			elif c == "\n":
				self.processLineFeed()
			elif c == "\x1b":
				c = yield from self.peekCharacter()
				if c == "[":
					self.advance()
					c = yield from self.peekCharacter()
					if c == "?": self.advance()
					
					c = yield from self.peekCharacter()
					if c == "A":
						self.advance()
						self.setCursorPos(self.cursorX, self.cursorY - 1)
					elif c == "B":
						self.advance()
						self.setCursorPos(self.cursorX, self.cursorY + 1)
					elif c == "C":
						self.advance()
						self.setCursorPos(self.cursorX + 1, self.cursorY)
					elif c == "D":
						self.advance()
						self.setCursorPos(self.cursorX - 1, self.cursorY)
					elif c == "H":
						self.advance()
						self.setCursorPos(0, 0)
					elif c == "J":
						self.advance()
						self.clearCharacterSpan(self.cursorY, self.cursorX, self.width)
						self.clearLineRange(self.cursorY + 1, self.height)
					elif c == "K":
						self.advance()
						self.clearCharacterSpan(self.cursorY, self.cursorX, self.width)
					else:
						nString = yield from self.readNumber()
						mString = ""
						
						semicolon = False
						if (yield from self.acceptCharacter(";")):
							semicolon = True
							mString = yield from self.readNumber()
						
						n = int(nString) if len(nString) > 0 else 1
						m = int(mString) if len(mString) > 0 else 1
						
						c = yield from self.peekCharacter()
						if c == "G":
							self.advance()
							self.setCursorPos(n - 1, self.cursorY)
						elif c == "H":
							self.advance()
							self.setCursorPos(m - 1, n - 1)
						elif c == "J":
							self.advance()
							if n == 0 or n == 1:
								rejectedString = "\\x1b[" + nString
								if semicolon:
									rejectedString += ";" + mString
								rejectedString += "J"
								self.writeString(rejectedString)
								
								if self.logger is not None:
									self.logger.log ("TerminalEmulator: Rejecting " + rejectedString)
							elif n == 2:
								self.reset()
						elif c == "K":
							self.advance()
							if n == 0:
								self.clearCharacterSpan(self.cursorY, self.cursorX, self.width)
							elif n == 1:
								self.clearCharacterSpan(self.cursorY, 0, self.cursorX)
							elif n == 2:
								self.clearLineRange(self, self.cursorY, self.cursorY + 1)
							else:
								raise RuntimeError()
						elif c == "P":
							self.advance()
							for x in range(0, n):
								del self.lines[self.cursorY][self.cursorX]
								self.lines[self.cursorY].append(" ")
						elif c == "d":
							self.advance()
							self.setCursorPos(self.cursorX, n - 1)
						elif c == "h" or c == "l" or c == "m" or c == "r":
							self.advance()
						else:
							rejectedString = "\\x1b[" + nString
							if semicolon:
								rejectedString += ";" + mString
							
							self.writeString(rejectedString)
							
							if self.logger is not None:
								self.logger.log("TerminalEmulator: Rejecting " + rejectedString + ("\\x%02x" % ord(c)) + " / " + c)
				elif c == ">" or c == "(":
					self.advance()
					pass
				else:
					rejectedString = "\\x1b" + c
					self.writeString(rejectedString)
					if self.logger is not None:
						self.logger.log("TerminalEmulator: Rejecting \\x1b" + ("\\x%02x" % ord(c)) + " / " + c)
			else:
				self.writeCharacter(c)
	
	# Input
	def advance(self):
		if self.peekBuffer is None:
			raise RuntimeError()
		
		self.peekBuffer = None
	
	@asyncio.coroutine
	def acceptByte(self, uint8):
		if uint8 == (yield from self.peekByte()):
			self.advance()
			return True
		
		return False
	
	@asyncio.coroutine
	def acceptCharacter(self, c):
		if c == (yield from self.peekCharacter()):
			self.advance()
			return True
		
		return False
	
	@asyncio.coroutine
	def peekByte(self):
		if self.peekBuffer == None:
			self.peekBuffer = yield
		return self.peekBuffer
	
	@asyncio.coroutine
	def peekCharacter(self):
		return chr((yield from self.peekByte()))
	
	@asyncio.coroutine
	def readByte(self):
		uint8 = yield from self.peekByte()
		self.advance()
		return uint8
	
	@asyncio.coroutine
	def readCharacter(self):
		return chr((yield from self.readByte()))
	
	@asyncio.coroutine
	def readNumber(self):
		number = ""
		while True:
			c = yield from self.peekCharacter()
			if not c.isdigit(): break
			
			self.peekBuffer = None
			number += c
		
		return number
	
	# Output
	def clearCharacterSpan(self, line, startColumn, endColumn):
		for x in range(startColumn, endColumn):
			self.lines[self.cursorY][x] = " "
	
	def clearLineRange(self, startLine, endLine):
		for y in range(startLine, endLine):
			self.lines[y] = [" "] * self.width
	
	def processCarriageReturn(self):
		self.cursorX = 0
	
	def processLineFeed(self):
		self.cursorX = 0
		self.cursorY += 1
		
		if self.cursorY >= self.height:
			del self.lines[0]
			self.lines.append([" "] * self.width)
			self.cursorY = self.cursorY - 1
	
	def writeCharacter(self, c):
		self.lines[self.cursorY][self.cursorX] = c
		
		self.cursorX += 1
		if self.cursorX >= self.width:
			self.processLineFeed()
	
	def writeString(self, s):
		for c in s:
			self.writeCharacter(c)
