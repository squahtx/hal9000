class Event(object):
	def __init__(self, name = "Event"):
		self.name = name
		
		self.callbacks = {}
		
		self.suppressed            = 0
		self.pendingDispatch       = False
		self.pendingDispatchArgs   = None
		self.pendingDispatchKwargs = None
	
	def addListener(self, name, callback = None):
		if callback is None:
			callback = name
		
		self.callbacks[name] = callback
	
	def removeListener(self, name):
		self.callbacks[name] = None
	
	def dispatch(self, *args, **kwargs):
		if self.suppressed > 0:
			self.pendingDispatch       = True
			self.pendingDispatchArgs   = args
			self.pendingDispatchKwargs = kwargs
			return
		
		for name, callback in self.callbacks.items():
			callback(*args, **kwargs)
	
	def suppress(self):
		self.suppressed += 1
	
	def unsuppress(self):
		self.suppressed -= 1
		if self.suppressed < 0: raise RuntimeError()
		
		if self.suppressed == 0 and \
		   self.pendingDispatch:
			self.pendingDispatch = False
			
			args   = self.pendingDispatchArgs
			kwargs = self.pendingDispatchKwargs
			
			self.pendingDispatchArgs   = None
			self.pendingDispatchKwargs = None
			
			self.dispatch(*args, **kwargs)
	
	def __call__(self, *args, **kwargs):
		self.dispatch(*args, **kwargs)
