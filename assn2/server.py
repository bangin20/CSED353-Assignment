from socket import *
import threading
import sys

def input_prompt(conn):
  while True:
    #get input to send
    message = input()
    if message == "quit":
      break #repeat until input "quit"
    conn.send(message.encode())
    print("I > " + message)
  #disconnect socket
  conn.close()

def server_main(host, port):
  #create socket for server
  sock = socket(AF_INET, SOCK_STREAM)
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
        print("\n<" + str(c_addr[0]) + "> : " + conn.recv(4096).decode())
        
    except:
      print("Error Occured Close socket")
      #disconnect socket
      conn.close()

  #disconnect socket
  sock.close()

if __name__ == "__main__":
  if len(sys.argv) != 3:
    print("[USAGE] : server.py [HOST_IPADDR] [PORT]")
  else:
    try:
      #get host and port
      port = int(sys.argv[2])
      server_main(sys.argv[1], port)
    except ValueError:
      print("PORT should be Integer Value")

