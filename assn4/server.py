from socket import *
import threading
import pyaudio
import sys
import cv2
import struct
import numpy as np
import time

def send_video(conn):
    cap = cv2.VideoCapture(0)
    init = False

    while(cap.isOpened()):
        ret, frame = cap.read()
        if(ret == True):
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            size = b''

            for i in frame.shape:
                #print(struct.pack(">L", i))
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
                pass

        else:
            break

    cap.release()


def receive_video(conn):

    try:
        frameshape = 1
        s = []

        for i in range(3):
            size = conn.recv(4)
            #print(size)
            #print(int(struct.unpack(">L", size)[0]), struct.unpack(">L", size)[0])
            s.append(int(struct.unpack(">L", size)[0]))
            frameshape = frameshape * int(struct.unpack(">L", size)[0])

        data = b''
        nextData = b''

        while True:
            r = conn.recv(100000)
            #print(len(data))
            if(len(r) < frameshape - len(data)):
                data += r
            else:
                k = frameshape-len(data)
                nextData += r[k:]
                data += r[:k]

                nparr = np.fromstring(data, np.uint8)
                #print(s)
                frame = nparr.reshape(tuple(s))
                #frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                cv2.imshow('frame', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                data = nextData
                nextData = b''

    except Exception as exception:
        print('' + type(exception).__name__)
        cv2.destroyAllWindows()
        conn.close()
        pass

    cv2.destroyAllWindows()



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


def server_main(host, port, port2, port3):
    # create socket for server
    sock = socket(AF_INET, SOCK_STREAM)
    sock2 = socket(AF_INET, SOCK_STREAM)
    sock3 = socket(AF_INET, SOCK_STREAM)

    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    CHUNK = 1024
    RATE = 44100

    p = pyaudio.PyAudio()

    send_stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input = True, frames_per_buffer=CHUNK)
    receive_stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output = True, frames_per_buffer=CHUNK)


    s_addr = (host, port)
    s2_addr = (host, port2)
    s3_addr = (host, port3)
    print("Server open with " + host + ":%d and %d and %d" % (port, port2, port3))

    # socket bind
    sock.bind(s_addr)
    sock2.bind(s2_addr)
    sock3.bind(s3_addr)

    # socket listen
    sock.listen(1)
    sock2.listen(1)
    sock3.listen(1)

    while True:
        # accept connection from client
        conn, c_addr = sock.accept()
        conn_audio, c_au_addr = sock2.accept()
        conn_video, c_vi_addr = sock3.accept()

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

            video_recv_thread = threading.Thread(target=receive_video, args=(conn_video,))
            video_send_thread = threading.Thread(target=send_video, args=(conn_video,))

            video_recv_thread.daemon = True
            video_send_thread.daemon = True

            video_recv_thread.start()
            video_send_thread.start()

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
    if len(sys.argv) != 5:
        print("[USAGE] : server.py [HOST_IPADDR] [TEXTPORT] [VOICEPORT] [VIDEOPORT]")  # check if ip and port are specifed
    else:
        try:
            # get host and port
            port = int(sys.argv[2])
            port2 = int(sys.argv[3])
            port3 = int(sys.argv[4])
            server_main(sys.argv[1], port, port2, port3)  # call main network main function
        except ValueError:
            print("PORT should be Integer Value")
