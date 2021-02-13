from  tkinter import *
from ClienteInterfaz import ClienteInterfaz
import socket
import pickle
import select

if __name__ == '__main__':	
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = ('localhost', 5000)
	root = Tk()
	cliente = ClienteInterfaz(root,sock,server_address)
	while True:
		root.update()
		ready = select.select([sock], [], [], 0.02)
		if ready[0]:
			informacion, server = sock.recvfrom(4096)
			info = pickle.loads(informacion)
			if info[0] == 0:
				cliente.actualizalibro(info[1],info[2], info[3])
			if info[0] == 1:
				cliente.limpialibro()
			if info[0] == 2:
				cliente.reinicio()

