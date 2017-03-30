import socket
import time
from array import array
import struct
#reference to https://wiki.scratch.mit.edu/wiki/Communicating_to_Scratch_via_Python
class ScratchError(Exception):
	pass

class Py2Scratch14():
	def __init__(self,host='localhost',port=42001):
		#the first 4-byte of message contains size of the real message 
		#<4 bytes : size><message>
		self.prefix_len = 4
		self._port = port
		self._host = host
		self._socket = None
		
	def connect(self):
		try:
			self._socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			self._socket.connect((self._host,self._port))
			#self._socket.create_connection(address=(self._host,self._port),timeout=30)
		except socket.error as err :
			self._socket = None
			print( err)
			raise
			
	def close(self):
		if self._socket is not None :
			self._socket.close()
				
	def send(self,cmd):
		if self._socket is None :
			return
		try:
			n = len(cmd)
			#to create first 4 bytes
			a = array('u') #array of unicode
			a.append(chr((n >> 24) & 0xFF)) # first left most byte
			a.append(chr((n >> 16) & 0xFF)) # second byte
			a.append(chr((n >> 8) & 0xFF)) # third byte
			a.append(chr(n & 0xFF)) # forth byte
			self._socket.send(a.tostring() + cmd)
		except socket.error as err:
			print(err)
			raise
		
	def sendCMD(self,cmd):
		#this can be used with Python3
		if self._socket is None :
			return
		try:
			# first 4 bytes contains size of message	
			self._socket.send(len(cmd).to_bytes(4, 'big'))
			# then send the command to Scracth
			self._socket.send(bytes(cmd,'UTF-8'))
		except socket.err as err:
			print(err)
			raise
		

		
	def _read(self, size):
		"""
		Reads size number of bytes from Scratch and returns data as a string
		"""
		
		data = b''
		while len(data) < size:
			try:
				chunk = self._socket.recv(size-len(data))
			except socket.error :
				pass
			if chunk == '':
				pass
			data += chunk
		return data


	def _recv(self):
		"""
		Receives and returns a message from Scratch
		"""
		prefix = self._read(self.prefix_len)	
		msg = self._read(self._extract_len(prefix))
		
		#return prefix + msg
		return msg
		
	def receive(self):
		in_msg = self._recv().decode('UTF-8')  
		return self._parse(in_msg)
		#return in_msg
		
	def _extract_len(self, prefix): 
		"""
		Extracts the length of a Scratch message from the given message prefix. 
		"""
		return struct.unpack(">L", prefix)[0]	
		
	def _parse(self, msg):
		#print(msg)
		msg = msg.replace('"','')
		splited = msg.split(" ")
		'''
		msg_type = splited[0]
		msg_data = splited[1]		
		return (msg_type,msg_data)
		'''
		if len(splited) == 2 :
			return (splited[0],splited[1],None)
		else:
			return (splited[0],splited[1],splited[2])
		
	def sensorupdate(self, data):
		"""
		Given a dict of sensors and values, updates those sensors with the 
		values in Scratch.
		"""
		if isinstance(data, dict):
			msg = 'sensor-update '
			for key in data.keys():
				msg += '"%s" "%s" ' % (str(key), str(data[key]))
			self.sendCMD(msg)	
		
	def broadcast(self,msg):
		_msg = 'broadcast "'+msg+'"'
		self.sendCMD(_msg)		
	
if __name__ == "__main__":
	sc = Py2Scratch14(host='192.168.2.100')
	sc.connect()
	sc.broadcast("Hello")
	#print(sc._parse(sc.receive()))
	sc.sensorupdate({'temperature' : 75})
