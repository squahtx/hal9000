from .internedcollection import InternedCollection

class InternedNamedCollection(InternedCollection):
	def __init__(self, factory, identity = None):
		super(InternedNamedCollection, self).__init__(factory, identity)
		
		self.itemsByName = {}
	
	# InternedCollection
	# Internal
	def onItemAdded(self, item):
		super(InternedNamedCollection, self).onItemAdded(item)
		
		self.itemsByName[item.name] = item
	
	def onItemRemoved(self, item):
		super(InternedNamedCollection, self).onItemRemoved(item)
		
		if self.itemsByName[item.name] != item: return
		del self.itemsByName[item.name]
	
	# InternedNamedCollection
	def getByName(self, name, default = None):
		return self.itemsByName.get(name, default)
