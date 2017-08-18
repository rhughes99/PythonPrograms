"""
Socket wrapper for coroutines.

Python Essential Reference, page 465.
Last touched: 08/18/2017
"""

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
