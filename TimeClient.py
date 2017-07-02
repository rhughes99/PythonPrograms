# TimeClient.py
# from page 451

from socket import *
s = socket(AF_INET,SOCK_STREAM)		# create TCP socket
s.connect(('10.0.0.12',8888))		# connect to server
tm = s.recv(1024)					# receive no more than 1024 bytes
s.close
print("The time is %s" % tm.decode('ascii'))


