import functools

def abstract(f):
	@functools.wraps(f)
	def abstract(*args, **kwargs):
		f(*args, **kwargs)
		raise NotImplementedError()
	
	return abstract
