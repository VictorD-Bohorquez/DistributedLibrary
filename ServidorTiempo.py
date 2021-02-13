import socket, random
import sys
import pickle
import select
import time
from datetime import datetime
import mysql.connector

def UTC():
	now = datetime.now()
	hora =[int(now.hour),int(now.minute),int(now.second),1]
	return hora

def conexion():
	conexion=mysql.connector.connect(host="localhost", user="root", passwd="psw", database="horas")
	return conexion

def registar(ipa, hip, hserver):
	con = conexion()
	dip = str(ipa[0])
	sql = """insert into Registro (ip,horaIP,horaServidor) values(%s,%s,%s)"""
	cursor = con.cursor(prepared=True)
	cursor.execute(sql,(dip,hip,hserver))
	con.commit()
	con.close()

if __name__ == '__main__':
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = ('192.168.1.70', 10000)
	print('Servidor iniciado {} en el puerto {}'.format(*server_address))
	sock.bind(server_address)
	servidores = []
	inicial = datetime.now()
	validar = datetime.now()
	while True:
			ready = select.select([sock], [], [], 0.02)
			if ready[0]:
				data, address = sock.recvfrom(4096)
				if address in servidores:
					peticion = pickle.loads(data)
					if peticion[0] == 0:
						hour = UTC();
						paquete = pickle.dumps([1,(time.time()*1000)])
						sent = sock.sendto(paquete, address)
						h = str(peticion[1][0])+" : "+str(peticion[1][1])+" : "+str(peticion[1][2])
						hs = str(hour[0])+" : "+str(hour[1])+" : "+str(hour[2])
						registar(address,h,hs)
					if peticion[0] == 5:
						servidores.remove(address)
						print("El servidor "+ str(address) + " se ha desconectado")
				else:
					servidores.append(address)
					print("Nuevo servidor de libros: " + str(address))
					hora=random.randint(0,23)
					minuto=random.randint(0,59)
					seg=random.randint(0,59)
					lista = [hora,minuto,seg,1]
					inicio = pickle.dumps(lista)
					sent = sock.sendto(inicio, address)
			fin = datetime.now()
			validarfin = datetime.now()
			tiempo = fin - inicial
			validacion = validarfin - validar
			if tiempo.seconds >= 30:
				for servidor in servidores:
					peticion = pickle.dumps([0,"hora"])
					sent = sock.sendto(peticion, servidor)
				inicial = datetime.now()
			if validacion.seconds >= 60:
				for serv in servidores:
					request = pickle.dumps([2,"BD"])
					envio = sock.sendto(request, serv)
				validar = datetime.now()



