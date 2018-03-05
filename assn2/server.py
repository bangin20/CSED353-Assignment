from socket import *
import threading
import sys

def input_prompt(conn):
  while True:
    message = input()
    if message == "quit":
      break
    conn.send(message.encode())
    print("I > " + message)
  conn.close()

def server_main(host, port):
  sock = socket(AF_INET, SOCK_STREAM)
  s_addr = (host, port)
  print("Server open with " + host + ":%d" % (port))
  sock.bind(s_addr)

  sock.listen(1)
  while True:
    conn, c_addr = sock.accept()
    try:
      print("Client " + str(c_addr))
      t = threading.Thread(target = input_prompt, args=(conn,))
      t.daemon = True
      t.start()

      while True:
        print("\n<" + str(c_addr[0]) + "> : " + conn.recv(4096).decode())
    except:
      print("Error Occured Close socket")
      conn.close()

  sock.close()

if __name__ == "__main__":
  if len(sys.argv) != 3:
    print("[USAGE] : server.py [HOST_IPADDR] [PORT]")
  else:
    try:
      port = int(sys.argv[2])
      server_main(sys.argv[1], port)
    except ValueError:
      print("PORT should be Integer Value")

