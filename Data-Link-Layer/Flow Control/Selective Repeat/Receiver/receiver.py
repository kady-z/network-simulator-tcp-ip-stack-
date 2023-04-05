import socket
import time
import random
import threading

SERVER = "127.0.1.1"
PORT = 12345
ADDR = (SERVER,PORT)
FORMAT = "utf-8"
m = 2
next = 0
FINISHED = False
WINDOW_SIZE = 2**(m-1)
WINDOW_L = 0
WINDOW_R = WINDOW_SIZE-1
ACK_ARRAY = [False for i in range(2**m)]
DATA_BUFFER = ["" for i in range(2**m)]

receiver = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
receiver.connect(ADDR)

def sendAck(index):
	global FINISHED
	try:
		print(f"sending Acknowledgement {index}...")
		if not(FINISHED) and random.randint(0,100)%10==0 and False:
			pass
		else:
			ack = str(bin(index)).replace("0b","")
			ack = (13-len(ack))*' '+ack
			time.sleep(0.1)
			receiver.send(ack.encode(FORMAT))
	except:
		FINISHED = True
		print("Receiving finished...")
		print("Connection closed...")


def slideWindow(file):
	global FINISHED
	try:
		global WINDOW_L
		global WINDOW_R
		global m
		global ACK_ARRAY
		global DATA_BUFFER
		while not(FINISHED):
			if ACK_ARRAY[WINDOW_L]:
				file.write(DATA_BUFFER[WINDOW_L])
				WINDOW_L = (WINDOW_L+1)%(2**m)
				WINDOW_R = (WINDOW_R+1)%(2**m)
				ACK_ARRAY[WINDOW_R] = False
				DATA_BUFFER[WINDOW_R] = ""
	except:
		FINISHED = True
		print("Receiving finished...")
		print("Connection closed...")


def recvData(sendAck):
	global FINISHED
	try:
		global ACK_ARRAY
		global DATA_BUFFER
		while not(FINISHED):
			msg = receiver.recv(20).decode(FORMAT)
			index = int(msg[0:13],2)
			data = chr(int(msg[13:],2))
			ACK_ARRAY[index] = True
			DATA_BUFFER[index] = data
			print(f"message received {index}...{data}...Saving...")
			sendAckThread = threading.Thread(target=sendAck,args=(index,))
			sendAckThread.start()
	except:
		FINISHED = True
		print("Receiving finished...")
		print("Connection closed...")



try:
	file = open("random.txt",'w')
	recvDataThread =  threading.Thread(target=recvData,args=(sendAck,))
	slideWindowThread = threading.Thread(target=slideWindow,args=(file,))

	recvDataThread.start()
	slideWindowThread.start()

	recvDataThread.join()
	slideWindowThread.join()
except:
	FINISHED = True
	print("Receiving finished...")
	print("Connection closed...")
