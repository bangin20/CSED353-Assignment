#!/usr/bin/python3	

import socket
import cv2
import numpy as np
import pyaudio
import threading
import sys
import struct
import time

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


def receive_video(conn):

	try:
		frameshape = 1
		s = []

		for i in range(3):
			size = conn.recv(4)
			s.append(int(struct.unpack(">L", size)[0]))
			frameshape = frameshape * int(struct.unpack(">L", size)[0])
			#print(int(struct.unpack("<L", size)[0]))

		data = b''
		nextData = b''

		while True:
			r = conn.recv(100000)
			if(len(r) < frameshape - len(data)):
				data += r
			else:
				k = frameshape - len(data)
				nextData += r[k:]
				data += r[:k]

				nparr = np.fromstring(data, np.uint8)
				frame = nparr.reshape(tuple(s))
				
				cv2.imshow('frame', frame)

				if cv2.waitKey(1) & 0xFF == ord('q'):
					break
				data = nextData
				nextData = b''

	except Exception as exception:
		print(''+ type(exception).__name__)
		cv2.destroyAllWindows()
		conn.close()
		pass

	cv2.destroyAllWindows()


def send_video(conn):
	cap = cv2.VideoCapture(0)
	init = False

	while(cap.isOpened()) :
		ret, frame = cap.read()
		if ret == True:
			frame = cv2.flip(frame, 1)
			frame = cv2.resize(frame, None, fx = 0.5, fy = 0.5, interpolation=cv2.INTER_AREA)
			size = b''

			for i in frame.shape:
				size += struct.pack(">L", i)
			
			try:
				if(init == False):
					conn.send(size)
					init = True
				conn.send(frame)
				time.sleep(0.034)

				if cv2.waitKey(1) & 0xFF == ord('q'):
					break
			except Exception as exception:
				print('' + type(exception).__name__)
				cap.release()
				conn.close()

		else:
			break

	cap.release()


def main(host, port1, port2, port3):
	#create socket for client
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	voiceSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	videoSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	#connect to host
	port1 = int(port1)	#port for text
	port2 = int(port2)	#port for voice
	port3 = int(port3)
	clientSocket.connect((host, port1))
	voiceSocket.connect((host, port2))
	videoSocket.connect((host, port3))

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

	#make a thread to receiving video
	rv = threading.Thread(target = receive_video, args=(videoSocket, ))
	rv.daemon = True
	rv.start()
	#make a thread to sending video
	sv = threading.Thread(target = send_video, args=(videoSocket, ))
	sv.daemon = True
	sv.start()

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
	videoSocket.close()

if __name__ == "__main__":
	if len(sys.argv) != 5:
		print("[USAGE] : client.py [HOST_IPADDR] [PORT] [PORT] [PORT]")
	else:
		#get host and port
		main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])