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
