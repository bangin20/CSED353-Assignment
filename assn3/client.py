#!/usr/bin/python3

import socket
import pyaudio
import threading
import sys

# record
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

def receive_audio(s, received_au):
	while True:
		try:
			#receive voice from server
			data = s.recv(1024)
			received_au.write(data)
		except:
			break

def send_audio(s, sending_au):
	while True:
		try:
			#send voice to server
			data = sending_au.read(CHUNK)
			s.sendall(data)
		except:
			break

def send_mss(conn):
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

def main(host, port1, port2):
	#create socket for client
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	voiceSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	#connect to host
	port1 = int(port1)	#port for text
	port2 = int(port2)	#port for voice
	clientSocket.connect((host, port1))
	voiceSocket.connect((host, port2))

	#make audio instances
	audio = pyaudio.PyAudio()
	received_au = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
	sending_au = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

	#make a thread to get sending input
	t = threading.Thread(target = send_mss, args=(clientSocket,))
	t.daemon = True
	t.start()

	#make a thread to receiving voice
	ra = threading.Thread(target = receive_audio, args=(voiceSocket, received_au))
	ra.daemon = True
	ra.start()
	#make a thread to sending voice
	sa = threading.Thread(target = send_audio, args=(voiceSocket, sending_au))
	sa.daemon = True
	sa.start()

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

	while True:
		a = 1
		
	#disconnect socket
	clientSocket.close()
	voiceSocket.close()

if __name__ == "__main__":
	if len(sys.argv) != 4:
		print("[USAGE] : client.py [HOST_IPADDR] [PORT] [PORT]")
	else:
		#get host and port
		main(sys.argv[1], sys.argv[2], sys.argv[3])