from .event import Event

class InternedCollection(object):
	def __init__(self, factory, identity = None):
		super(InternedCollection, self).__init__()
		
		if identity is None: identity = lambda x: x
		
		self._itemAdded   = Event("itemAdded")
		self._itemRemoved = Event("itemRemoved")
		
		self.factory      = factory
		self.identity     = identity
		
		self.items        = {}
	
	def __getitem__(self, id):
		return self.items[id]
	
	def __iter__(self):
		return iter(self.items.values())
	
	def __len__(self):
		return len(self.items)
	
	# Events
	@property
	def itemAdded(self):
		return self._itemAdded
	
	@property
	def itemRemoved(self):
		return self._itemRemoved
	
	# Collection
	def clear():
		removedIds = list(self.items.keys)
		[self.remove(self.items[id]) for id in removedIds]
	
	def get(self, id, default = None):
		return self.items.get(id, default)
	
	def intern(self, item):
		return self.add(item)
	
	def inject(self, item, id = None):
		if id is None: id = self.identity(item)
		
		if id in self.items: self.remove(self.items[id])
		
		self.items[id] = item
		
		self.onItemAdded(item)
		self.itemAdded(item)
		
		return item
	
	def update(self, enumerable):
		ids = set()
		[ids.add(self.identity(item)) for item in enumerable]
		[self.intern(item)            for item in enumerable]
		
		removedIds = [id for id in self.items.keys() if id not in ids]
		[self.remove(self.items[id]) for id in removedIds]
	
	# Internal
	def onItemAdded(self, item): pass
	def onItemRemoved(self, item): pass
	
	# Internal
	def add(self, item):
		id = self.identity(item)
		if id in self.items: return self.items[id]
		
		item = self.factory(item)
		self.items[id] = item
		
		self.onItemAdded(item)
		self.itemAdded(item)
		
		return item
	
	def remove(self, item):
		id = self.identity(item)
		if id not in self.items: return
		
		del self.items[id]
		
		self.onItemRemoved(item)
		self.itemRemoved(item)
