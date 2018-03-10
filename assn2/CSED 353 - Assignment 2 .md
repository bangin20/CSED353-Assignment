# <div style="text-align: center"> CSED 353 - Assignment 2 </div>
### <div style="text-align: center">  Simple Chatting Program </div>

### <div style="text-align: right"> 20140753 백우정, 20140407 송창훈</div>

---

### 1. Design
- 사용언어 : Python3
- socket 종류 : stream
- 구성 : server.py, client.py
    - 각각 server와 client에 관한 python코드
- server.py
    - socket을 만든 후, client와 연결 (socket, bind, listen, accept 함수)
    - client로부터 message를 받아와 출력 (recv 함수)
    - server의 message를 client에 전달 (send 함수)
    - recv, send는 각각 다른 thread에서 진행 (threading library)
    - 연결이 끊어지지 않으면 계속해서 message를 보내거나 받을 수 있음
- cliend.py
    - socket을 만든 후, server와 연결 (socket, connect 함수)
    - server로부터 message를 받아와 출력 (recv 함수)
    - client의 message를 server에 전달 (send 함수)
    - recv, send는 각각 다른 thread에서 진행 (threading library)
    - 연결이 끊어지지 않으면 계속해서 message를 보내거나 받을 수 있음

### 2. Source Code

* #### server.py
```python
#!/usr/bin/python3

from socket import *
import threading
import sys

def input_prompt(conn):  # thread function to get input from keyboard
  while True:
    #get input to send
    message = input()
    if message == "quit":
      break               #repeat until input "quit"
    conn.send(message.encode())
    print("I > " + message)
  #disconnect socket
  conn.close()

def server_main(host, port):
  #create socket for server
  sock = socket(AF\_INET, SOCK\_STREAM)
  s_addr = (host, port)
  print("Server open with " + host + ":%d" % (port))
  
  #socket bind
  sock.bind(s_addr)

  #socket listen
  sock.listen(1)
  while True:
    #accept connection from client
    conn, c_addr = sock.accept()
    try:
      print("Client " + str(c_addr))
      
      #make a thread to get sending input
      t = threading.Thread(target = input_prompt, args=(conn,))
      t.daemon = True
      t.start()

      #receive message
      while True:
        #print received message
        print("\\n<" + str(c_addr\[0\]) + "> : " + conn.recv(4096).decode())
        
    except:
      print("Error Occured Close socket")
      #disconnect socket
      conn.close()

  #disconnect socket
  sock.close()

if __name__ == "__main__":  # main function
  if len(sys.argv) != 3:
    print("[USAGE] : server.py [HOST_IPADDR] [PORT]")  # check if ip and port are specifed
  else:
    try:
      #get host and port
      port = int(sys.argv[2])
      server_main(sys.argv[1], port)                   # call main network main function
    except ValueError:
      print("PORT should be Integer Value")
```

* ### client.py

```python
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
```


### 3. Execution Video

### 4. Conclusion

Python을 이용하여, stream socket으로 구성된 간단한 chat application을 만들어보았다.
현재 완벽히 CUI 환경에서 작동하는 chat module이기 때문에, input, output간에 겹치는 문제가 있지만, GUI가 없던 시절이라고 생각하면 완벽한 채팅 프로그램의 기능을 수행하는 Application을 완성시켰다.