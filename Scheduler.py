"""
I/O-based task scheduler for coroutines.

Python Essential Reference, page 460.
Last touched: 08/18/2017
"""

import select
import types
import collections

# Socket object wrapper
class CoSocket(object):
	def __init__(self,sock):
		self.sock = sock
	def close(self):
		yield self.sock.close()
	def bind(self,addr):
		yield self.sock.bind(addr)
	def listen(self,backlog):
		yield self.sock.listen(backlog)
	def connect(self,addr):
		yield WriteWait(self.sock)
		yield self.sock.connect(addr)
	def accept(self):
		yield ReadWait(self.sock)
		conn, addr = self.sock.accept()
		yield CoSocket(conn), addr
	def send(self,data):
		while data:
			evt = yield WriteWait(self.sock)
			nsent = self.sock.send(data)
			data = data[nsent:]
	def recv(self,maxsize):
		yield ReadWait(self.sock)
		yield self.sock.recv(maxsize)

# Object that represents a running task
class Task(object):
	def __init__(self,target):
		self.target	 = target	# a coroutine
		self.sendval = None		# value to send when resuming
		self.stack	 = []		# call stack	
	def run(self):
		try:
			result = self.target.send(self.sendval)
			if isinstance(result,SystemCall):
				return result
			if isinstance(result,types.GeneratorType):
				self.stack.append(self.target)
				self.sendval = None
				self.target = result
			else:
				if not self.stack: return
				self.sendval = result
				self.target = self.stack.pop()
		except StopIteration:
			if not self.stack: raise
			self.sendval = None
			self.target = self.stack.pop()

# Object that represents a "system call"
class SystemCall(object):
	def handle(self,sched,task):
		pass

# Scheduler object
class Scheduler(object):
	def __init__(self):
		self.task_queue		= collections.deque()
		self.read_waiting	= {}
		self.write_waiting	= {}
		self.numtasks		= 0
	
	# Create new task out of a coroutine
	def new(self,target):
		newtask = Task(target)
		self.schedule(newtask)
		self.numtasks += 1
	
	# Put task on task queue
	def schedule(self,task):
		self.task_queue.append(task)
	
	# Have task wait for data on a file descriptor
	def readwait(self,task,fd):
		self.read_waiting[fd] = task
	
	# Have task wait for writing on a file descriptor
	def writewait(self,task,fd):
		self.write_waiting[fd] = task
	
	# Main schedule loop
	def mainloop(self,count=-1,timeout=None):
		while self.numtasks:
			# Check for I/O events to handle
			if self.read_waiting or self.write_waiting:
				wait = 0 if self.task_queue else timeout
				r,w,e = select.select(self.read_waiting, self.write_waiting, [], wait)
				for fileno in r:
					self.schedule(self.read_waiting.pop(fileno))
				for fileno in w:
					self.schedule(self.write_waiting.pop(fileno))
			
			# Run all tasks on queue that are ready to run
			while self.task_queue:
				task = self.task_queue.popleft()
				try:
					result = task.run()
					if isinstance(result,SystemCall):
						result.handle(self,task)
					else:
						self.schedule(task)
				except StopIteration:
					self.numtasks -= 1
			
			# If no tasks can run, decided if we wait or return
			else:
				if count > 0: count -= 1
				if count == 0:
					return

# Implementation of different system calls
class ReadWait(SystemCall):
	def __init__(self,f):
		self.f = f
	def handle(self,sched,task):
		fileno = self.f.fileno()
		sched.readwait(task,fileno)

class WriteWait(SystemCall):
	def __init__(self,f):
		self.f = f
	def handle(self,sched,task):
		fileno = self.f.fileno()
		sched.writewait(task,fileno)

class NewTask(SystemCall):
	def __init__(self,target):
		self.target = target
	def handle(self,sched,task):
		sched.new(self.target)
		sched.schedule(task)
