import socket
import time
import random

SERVER = "127.0.1.1"
PORT = 12345
ADDR = (SERVER,PORT)
RTT = 0.1
TIMEOUT = RTT*2
FORMAT = "utf-8"
next = 0
FINISHED = False

receiver = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
receiver.connect(ADDR)

def sendAck():
	global next
	time.sleep(RTT/2)
	if not(FINISHED) and random.randint(0,100)%10==0:
		pass
	else:
		receiver.send(str(next).encode(FORMAT))
	print(f"sending Acknowledgement {next}...")


try:
	file = open("random.txt",'w')
	next = 0
	while not(FINISHED):
		msg = receiver.recv(8).decode(FORMAT)
		print(f"message received {chr(int(msg[1:],2))}...{msg[1:]}")
		if(int(msg[0])!=next):
			print("previos message received...Discarding...")
		elif chr(int(msg[1:],2))=='~':
			FINISHED = True
			next = 1 - next
			sendAck()
			receiver.close()
			file.close()
			print("Receiving finished...")
			print("Connection closed...")
			break
		else:
			print("Expected message received...Saving...")
			file.write(chr(int(msg[1:],2)))
			next = 1 - next
		sendAck()
except:
	print("Receiving finished...")
	print("Connection closed...")
