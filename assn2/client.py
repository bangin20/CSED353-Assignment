#!/usr/bin/python3

import socket
import threading
import sys

def send(conn):
	#get input to send
	sending = input("Send : ")

	while sending != "quit": #repeat until input "quit"
		try:
			#send message to server
			conn.send(sending.encode('ascii'))
			#get input to send again
			sending = input("Send : ")

		except Exception as exception:
			print(''+ type(exception).__name__)
			break

	#disconnect socket
	conn.close()

def main(host, port):
	#create socket for client
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	#connect to host
	port = int(port)
	clientSocket.connect((host, port))

	#make a thread to get sending input
	t = threading.Thread(target = send, args=(clientSocket,))
	t.daemon = True
	t.start()

	#receive message
	while True:
		try:
			#receive message from server
			received = clientSocket.recv(4096)
			if not received: #no received message
				print("Server closed")
				break
			else: #print received message
				print('\nFrom server : ' + received.decode())

		except Exception as exception:
			print(''+ type(exception).__name__)
			break

	#disconnect socket
	clientSocket.close()

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("[USAGE] : client.py [HOST_IPADDR] [PORT]")
	else:
		#get host and port
		main(sys.argv[1], sys.argv[2])