#!/usr/bin/env python
# encoding:utf-8
__author__ = 'SY60216'

import sqlite3,sys,re
import SocketServer
from SocketServer import StreamRequestHandler as SRH
from time import ctime

host = '0.0.0.0'
port = 9716
addr = (host,port)

class Servers(SRH):
	def handle(self):
		print 'got connection from ',self.client_address
		#self.wfile.write('connection %s:%s at %s succeed!' % (host,port,ctime()))
		while True:
			data = self.request.recv(1024)
			if data=="close" or not data: 
				break
			elif data.find("get")!=-1:
				conn = sqlite3.connect("/home/nagios/modError.db")
				cur = conn.cursor()
				try:
					n=cur.execute("select * from modError;")
					result = cur.fetchall()
					new_list = ""
					for inv in result:
						d = ""
						for i in range(0,len(inv)):
							d = d + "-" + inv[i]
						d = re.sub(r'^-',"",d,0)
						new_list = new_list + "|" + d
					new_list = re.sub(r'^\|',"",new_list,0)
				except sqlite3.Error,e:
					print "sqlite Error:%s\nSQL:%s" %(e,sql)
				if new_list != "":
					#self.request.send(new_list)
					self.wfile.write('%s\n' %new_list)
					print new_list
				else:
					self.request.send("OK\n")
					print "everything is ok!"
			else:
				print "rev:",data
				print "RECV from ", self.client_address[0]
				self.request.send("error\n")
		print 'close connection ',self.client_address

#t = SQLClass()
print 'server is running....'
server = SocketServer.ThreadingTCPServer(addr,Servers)
server.serve_forever()



