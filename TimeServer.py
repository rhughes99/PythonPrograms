# Time server program
# Page 451
from socket import *
import time

s = socket(AF_INET, SOCK_STREAM)	# create TCP socket
s.bind(('',8888))			# bind to port 8888
s.listen(2)				# listen, but allow no more than 2 pending connections

while True:
	client,addr = s.accept()	# get a connection
	print("Got a connection from %s" % str(addr))
	timestr = time.ctime(time.time()) + "\r\n"
	client.send(timestr.encode('ascii'))
	client.close()
