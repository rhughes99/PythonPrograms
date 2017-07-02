# asynchatServer.py
# from page 453
# An asynchronous HTTP server using asnychat

import asynchat, asyncore, socket
import os
import mimetypes
try:
	from http.client import responses	# Python 3
except ImportError:
	from httplib import responses		# Python 2

# This class plugs into the asyncore module and handles accept events
class async_http(asyncore.dispatcher):
	def __init__(self,port):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET,socket.SOCK_STREAM)
		self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.bind(('',port))
		self.listen(5)
	
	def handle_accept(self):
		client,addr = self.accept()
		return async_http_handler(client)

# Class that handles asynchronous HTTP requests
class async_http_handler(asynchat.async_chat):
	def __init__(self,conn=None):
		asynchat.async_chat.__init__(self,conn)
		self.data = [];
		self.got_header = False
		self.set_terminator(b"\r\n\r\n")
	
	# Get incoming data and append to data buffer
	def collect_incoming_data(self,data):
		if not self.got_header:
			self.data.append(data)
	
	# Got a terminator (blank line)
	def found_terminator(self):
		self.got_header = True
		header_data = b"".join(self.data)
		# Decode header data (binary) into text for further processing
		header_text = header_data.decode('latin-1')
		header_lines = header_text.splitlines()
		request = header_lines[0].split()
		op = request[0]
		url = request[1][1:]
		self.process_request(op,url)
	
	# Push text onto outgoing stream, but encode it first
	def push_text(self,text):
		self.push(text.encode('latin-1'))
	
	# Process request
	def process_request(self, op, url):
		if op == "GET":
			if not os.path.exits(url):
				self.send_error(404,"File %s not found\r\n")
			else:
				type, encoding = mimetypes.guess_type(url)
				size = os.path.getsize(url)
				self.push_text("HTTP/1.0 200 OK\r\n")
				self.push_text("Content-length: %s\r\n" % size)
				self.push_text("Content-type: %s\r\n" % type)
				self.push_text("\r\n")
				self.push_with_producer(file_producer(url))
		else:
			self.send_error(501,"%s method not implemented" % op)
		self.close_when_done();
	
	# Error handling
	def send_error(self,code,message):
		self.push_text("HTTP/1.0 %s %s\r\n" % (code, responses[code]))
		self.push_text("Content-type: text/plain\r\n")
		self.push_text("\r\n")
		self.push_text(message)

class file_producer(object):
	def __init__(self,filename,buffer_size=512):
		self.f = open(filename,"rb")
		self.buffer_size = buffer_size
	def more(self):
		data = self.f.read(self.buffer_size)
		if not_data:
			self.f.clos()
		return data

a = async_http(8888)
asyncore.loop()

