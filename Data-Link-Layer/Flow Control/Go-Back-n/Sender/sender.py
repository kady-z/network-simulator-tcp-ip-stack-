import socket
import threading
import time
import random

sender = "0.0.0.0"
PORT = 12345
ADDR = (sender,PORT)
FORMAT = "utf-8"
STARTED = False
FINISHED = False
m = 2
WINDOW_SIZE = 2**m-1
WINDOW_L = 0
WINDOW_R = 2**m-2
index_L = 0
index_R = 2**m-2
RTT = 0.2
TIMEOUT = 2*RTT*m
MSG_LEN = 20
sender = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sender.bind(ADDR)
next = 0
global prevTime
prevTime = [time.time() for i in range(2**m)]

def sendData(s,conn,index):
    try:
        global m
        w = index%(2**m)
        msg = str(bin(ord(s[index])).replace("0b",""))
        msg = (7-len(msg))*' '+msg
        msg = str(bin(w).replace("0b",""))+msg
        msg = (MSG_LEN-len(msg))*' '+msg
        prevTime[w] = time.time()
        time.sleep(RTT/2)
        conn.send(msg.encode(FORMAT))
    except:
        global FINISHED
        FINISHED = True
        print("sending finished...")
        print("Connection closed...")

def sendWindow(s,conn,l,r):
    try:
        for i in range(l,r+1):
            time.sleep(0.01)
            sendDataThread = threading.Thread(target=sendData,args=(s,conn,i))
            sendDataThread.start()
    except:
        global FINISHED
        FINISHED = True
        print("sending finished...")
        print("Connection closed...")


def recvAck(s,conn,sendWindow):
    global FINISHED
    global m
    global WINDOW_L
    global WINDOW_R
    global index_L
    global index_R
    while not(FINISHED):
        try:
            ack = int(conn.recv(13).decode(),2)
            if WINDOW_L<ack:
                diff = (ack-WINDOW_L)
            else:
                diff = (ack+2**m-WINDOW_L)
            WINDOW_L = (WINDOW_L+diff)%(2**m)
            WINDOW_R = (WINDOW_R+diff)%(2**m)
            index_L += diff
            index_R += diff
            print(f"Acknowledgement {ack} received")
            print(f"sending messages {(index_R-diff+1)%(2**m)} to {index_R%(2**m)}")
            sendWindow(s,conn,index_R-diff+1,index_R)
        except:
            FINISHED = True
            print("sending finished...")
            print("Connection closed...")


def checkTimeOut(s,conn,sendWindow):
    try:
        global FINISHED
        global WINDOW_L
        global WINDOW_R
        global index_L
        global index_R
        while not(FINISHED):
            if (time.time()-prevTime[WINDOW_L])>TIMEOUT:
                global STARTED
                if STARTED:
                    print("Time out!!!sending data again...")
                else:
                    STARTED = True
                print(f"sending window {WINDOW_L} to {WINDOW_R}")
                sendWindow(s,conn,index_L,index_R)
    except:
        FINISHED = True
        print("sending finished...")
        print("Connection closed...")



try:
    sender.listen(1)
    print("Waiting for receiver...")
    conn , addr = sender.accept()
    print("Connection established...")
    with open('random.txt') as file:
        s = file.read()
        prevTime = [time.time() for i in range(2**m)]
        checkTimeOutThread = threading.Thread(target=checkTimeOut,args=(s,conn,sendWindow))
        recvAckThread = threading.Thread(target=recvAck,args=(s,conn,sendWindow))

        checkTimeOutThread.start()
        recvAckThread.start()

        checkTimeOutThread.join()
        recvAckThread.join()
except:
    FINISHED = True
    print("sending finished...")
    print("Connection closed...")
