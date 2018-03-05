#!/usr/bin/python3

import socket
import threading
import sys

def send(conn):
	sending = input("Send : ")

	while sending != "quit":
		try:
			conn.send(sending.encode('ascii'))
			sending = input("Send : ")
		except Exception as exception:
			print(''+ type(exception).__name__)
			break
	conn.close()

def main(host, port):
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	port = int(port)
	clientSocket.connect((host, port))

	t = threading.Thread(target = send, args=(clientSocket,))
	t.daemon = True
	t.start()

	while True:
		try:
			received = clientSocket.recv(4096)
			if not received:
				print("Server closed")
				break
			else:
				print('\nFrom server : ' + received.decode())

		except Exception as exception:
			print(''+ type(exception).__name__)
			break


	clientSocket.close()

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("[USAGE] : client.py [HOST_IPADDR] [PORT]")
	else:
		main(sys.argv[1], sys.argv[2])