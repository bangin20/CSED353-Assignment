# <div style="text-align: center"> CSED 353 - Assignment 3 </div>

### <div style="text-align: center">  Simple Voice Chat Program </div>

### <div style="text-align: right"> 20140753 백우정, 20140407 송창훈</div>

------

### 1. Design

- 사용언어 : Python3
- socket 종류 : stream
- 구성 : server.py client.py
  - 각각 server와 client에 관한 python코드
- server.py
  - 사용 library
    - socket, threading, pyaudio, sys
  - socket을 만든 후, client와 연결 (socket, bind, listen, accept 함수)
    - socket 두 개를 각각 text, voice 용으로 사용
  - text 부분
    - client로부터 text를 받아와 출력 (recv 함수)
    - server의 text를 client에 전달 (send 함수)
  - voice 부분
    - send, receive에 대한 stream을 선언 (open 함수)
    - client로부터 voice를 받아와 출력 (recv, write 함수)
    - server의 voice를 client에 전달 (read, send 함수)
  - text 주기, 받기, voice 주기, 받기는 각각 다른 thread에서 진행 (threading library)
  - 연결이 끊어지지 않으면 계속해서 message를 보내거나 받을 수 있음
- client.py
  - 사용 library
    - socket, threading, pyaudio, sys
  - socket을 만든 후, server와 연결 (socket, connect 함수)
  - text 부분
    - server로부터 text를 받아와 출력 (recv 함수)
    - client의 text를 server에 전달 (send 함수)
  - voice 부분
    - send, receive에 대한 stream을 선언 (open 함수)
    - server로부터 voice를 받아와 출력 (recv, write 함수)
    - client의 voice를 client에 전달 (read, send 함수)
  - text 주기, 받기, voice 주기, 받기는 각각 다른 thread에서 진행 (threading library)
  - 연결이 끊어지지 않으면 계속해서 message를 보내거나 받을 수 있음

### 2. Source Code

- #### server.py

```python
from socket import *
import threading
import pyaudio
import sys


def receive_audio(conn, stream, chunk):
    while True:
        try:
            data = conn.recv(1024)
            stream.write(data)
        except:
            conn.close()
    conn.close()
    pass

def send_audio(conn, stream, chunk):
    while True:
        try:
            data = stream.read(chunk)
            conn.send(data)
        except:
            conn.close()
    conn.close()
    pass

def input_prompt(conn):  # thread function to get input from keyboard
    while True:
        # get input to send
        message = input()
        if message == "quit":
            break  # repeat until input "quit"
        conn.send(message.encode())
        print("I > " + message)
    # disconnect socket
    conn.close()
    pass


def server_main(host, port, port2):
    # create socket for server
    sock = socket(AF_INET, SOCK_STREAM)
    sock2 = socket(AF_INET, SOCK_STREAM)

    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    CHUNK = 1024
    RATE = 44100

    p = pyaudio.PyAudio()

    send_stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input = True, frames_per_buffer=CHUNK)
    receive_stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output = True, frames_per_buffer=CHUNK)


    s_addr = (host, port)
    s2_addr = (host, port2)
    print("Server open with " + host + ":%d and %d" % (port, port2))

    # socket bind
    sock.bind(s_addr)
    sock2.bind(s2_addr)

    # socket listen
    sock.listen(1)
    sock2.listen(1)
    while True:
        # accept connection from client
        conn, c_addr = sock.accept()
        conn_audio, c_au_addr = sock2.accept()
        try:
            print("Client " + str(c_addr))

            # make a thread to get sending input
            t = threading.Thread(target=input_prompt, args=(conn,))
            t.daemon = True
            t.start()

            receive_thread = threading.Thread(target=receive_audio, args=(conn_audio, receive_stream, CHUNK))
            receive_thread.daemon = True

            send_thread = threading.Thread(target=send_audio, args=(conn_audio, send_stream, CHUNK))
            send_thread.daemon = True

            receive_thread.start()
            send_thread.start()

            # receive message
            while True:
                # print received message
                #useless = 0
                print("\n<" + str(c_addr[0]) + "> : " + conn.recv(4096).decode())

        except:
            print("Error Occured Close socket")
            # disconnect socket
            conn.close()
            conn_audio.close()

    # disconnect socket
    sock.close()
    sock2.close()


if __name__ == "__main__":  # main function
    if len(sys.argv) != 4:
        print("[USAGE] : server.py [HOST_IPADDR] [PORT]")  # check if ip and port are specifed
    else:
        try:
            # get host and port
            port = int(sys.argv[2])
            port2 = int(sys.argv[3])
            server_main(sys.argv[1], port, port2)  # call main network main function
        except ValueError:
            print("PORT should be Integer Value")
```

- #### client.py

```python
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
```

### 3. Execution Video

### <font color="blue"> **Please check attached Video File** </font>

### 4. Conclusion

Python을 이용하여, stream socket 두 개로 구성된 간단한 voice chat application을 만들어 보았다. 말하는 동시에 stream이 전송되어 저장하여 보내는 것 보다 더욱 편리하다. 이와 함께 text로도 message를 주고 받을 수 있어 assignment의 요구사항을 만족시킨다.
