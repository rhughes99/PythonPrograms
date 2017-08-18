"""
Time client program. Gets time from TimeServer.py, prints it, and quits.

Example of TCP client/server protocol.
Python Essential Reference, page 451.
Last touched: 08/18/2017
"""

from socket import *
s = socket(AF_INET,SOCK_STREAM)		# create TCP socket
s.connect(('10.0.0.13',8888))		# connect to (wireless) server
tm = s.recv(1024)					# receive no more than 1024 bytes
s.close
print("The time is %s" % tm.decode('ascii'))

