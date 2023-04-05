import socket
import threading
import time
import random

sender = "0.0.0.0"
PORT = 12345
ADDR = (sender,PORT)
FORMAT = "utf-8"
RTT = 0.1
TIMEOUT = RTT*2
STARTED = False
FINISHED = False

sender = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sender.bind(ADDR)
next = 0
index = 0
global prevTime
prevTime = time.time()


def sendData(s,conn):
    global index
    global FINISHED
    msg = str(bin(ord(s[index])).replace("0b",""))
    msg = str(next) + msg
    time.sleep(RTT/2)
    if random.randint(0,10000)%54==0 and s[index]!='~':
        pass
    else:
        conn.send(msg.encode(FORMAT))
    if(s[index]=='~'):
        FINISHED =True
    if FINISHED:
        print("sending finished...")
        print("Connection closed...")
        conn.close()
        return
    print(f"sending...{s[index]}...{msg}")
    global prevTime
    prevTime = time.time()


def checkTimeOut(s,conn,sendData):
    global FINISHED
    while not(FINISHED):
        global prevTime
        currTime = time.time()
        if((currTime-prevTime)>TIMEOUT):
            global STARTED
            if STARTED:
                print("Time out!!!sending data again...")
            else:
                STARTED = True
            sendData(s,conn)

def recvAck(s,conn,sendData):
    global FINISHED
    while not(FINISHED):
        global index
        ack = int(conn.recv(1).decode())
        global next
        if ack != next:
            next = ack
            index += 1
        print(f"Acknowledgement {ack} received,sending data...")
        sendData(s,conn)
        prevTime = time.time()


sender.listen(1)
print("Waiting for receiver...")
conn , addr = sender.accept()
print("Connection established...")
with open('random.txt') as file:
    s = file.read()
    prevTime = time.time()
    index = 0
    checkTimeOutThread = threading.Thread(target=checkTimeOut,args=(s,conn,sendData))
    recvAckThread = threading.Thread(target=recvAck,args=(s,conn,sendData))

    checkTimeOutThread.start()
    recvAckThread.start()

    checkTimeOutThread.join()
    recvAckThread.join()
