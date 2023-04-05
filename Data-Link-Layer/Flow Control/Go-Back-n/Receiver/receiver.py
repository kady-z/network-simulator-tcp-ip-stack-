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

receiver = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
receiver.connect(ADDR)

def sendAck(nextExpected):
	global FINISHED
	try:
		print(f"sending Acknowledgement {nextExpected}...")
		if not(FINISHED) and random.randint(0,100)%10==0:
			pass
		else:
			ack = str(bin(nextExpected)).replace("0b","")
			ack = (13-len(ack))*' '+ack
			time.sleep(0.1)
			receiver.send(ack.encode(FORMAT))
	except:
		FINISHED = True
		print("Receiving finished...")
		print("Connection closed...")

try:
	file = open("random.txt",'w')
	next = 0
	while not(FINISHED):
		msg = receiver.recv(20).decode(FORMAT)
		if(int(msg[0:13],2)!=next):
			if next==(int(msg[0:13],2)+1)%(2**m):
				sendAckThread = threading.Thread(target = sendAck,args=(next,),daemon=True)
				sendAckThread.start()
			print(f"Expected message not received {int(msg[0:13],2)}...{chr(int(msg[13:],2))}...Discarding...")
		else:
			print(f"Expected message received {next}...{chr(int(msg[13:],2))}...Saving...")
			file.write(chr(int(msg[13:],2)))
			next = (next+1)%(2**m)
			sendAckThread = threading.Thread(target = sendAck,args=(next,))
			sendAckThread.start()
except:
	FINISHED = True
	print("Receiving finished...")
	print("Connection closed...")
