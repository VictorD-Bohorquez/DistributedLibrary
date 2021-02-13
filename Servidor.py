import socket
import sys
from ServidorLibros import ServidorLibros
import pickle
from  tkinter import *
import select
import time
import random
from datetime import datetime
import mysql.connector

def conexion():
	conexion=mysql.connector.connect(host="localhost", user="root", passwd="blackmaria", database="libros")
	return conexion

def obtenerlibros():
	con = conexion()
	cursor=con.cursor()
	cursor.execute("select nombre from libro where disponibilidad = 'S'")
	libros = []
	for libro in cursor:
		libros.append(libro[0])
	con.close()
	return libros

def obtenerportada(libro):
	con = conexion()
	sql = """select portada from Libro where nombre = %s"""
	cursor = con.cursor(prepared=True)
	cursor.execute(sql,(libro,))
	portada = cursor.fetchone()
	con.close()
	return portada[0]

def obtenerAutor(libro):
	con = conexion()
	sql = """select autor from Libro where nombre = %s"""
	cursor = con.cursor(prepared=True)
	cursor.execute(sql,(libro,))
	autor = cursor.fetchone()
	con.close()
	return autor[0]

def obtenerid(libro):
	con = conexion()
	sql = """select idLibro from Libro where nombre = %s"""
	cursor = con.cursor(prepared=True)
	cursor.execute(sql,(libro,))
	idlib = cursor.fetchone()
	con.close()
	return idlib[0]

def disponibilidad(libro):
	con = conexion()
	sql = """select disponibilidad from Libro where nombre = %s"""
	cursor = con.cursor(prepared=True)
	cursor.execute(sql,(libro,))
	disp = cursor.fetchone()
	con.close()
	return disp[0]

def cambiarDisponibilidad(libro):
	con = conexion()
	disponible = disponibilidad(libro)
	idlib = obtenerid(libro)
	if disponible == 'S':
		sql = """update Libro set disponibilidad = 'N' where idLibro = %s"""
	else:
		sql = """update Libro set disponibilidad = 'S' where idLibro = %s"""
	cursor = con.cursor(prepared=True)
	cursor.execute(sql,(idlib,))
	con.commit()
	con.close()


def reiniciar():
	con = conexion()
	cursor=con.cursor()
	cursor.execute("select nombre from libro")
	libros = []
	for libro in cursor:
		libros.append(libro[0])
	con.close()
	print ("Libros reiniciados")
	for lib in libros:
		cambiarDisponibilidad(lib)


def guardarPedido(ip,h,lib):
	con = conexion()
	dip = ip[0]
	idlib = obtenerid(lib)
	sql = """insert into Pedido (ip,hora,idLibro) values(%s,%s,%s)"""
	cursor = con.cursor(prepared=True)
	cursor.execute(sql,(dip,h,idlib))
	con.commit()
	con.close()

def actualizarCompanero(s,dirc,h,lib,comp):
	s.sendto(pickle.dumps([3,dirc,h,lib]),comp)


def cristian(tiempo,viaje):
	viaje = viaje * 1000
	viaje = viaje/2
	print(datetime.fromtimestamp(tiempo/1000.0))
	tiempo = tiempo + viaje
	print(datetime.fromtimestamp(tiempo/1000.0))
	date = datetime.fromtimestamp(tiempo/1000.0)
	hora =[int(date.hour),int(date.minute),int(date.second),1]
	return hora

if __name__ == '__main__':
	print(obtenerlibros())
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = ('localhost', 10000)
	partner_address= ('localhost',6000)
	socketLibros = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	libros_address = ('localhost', 5000)
	socketLibros.bind(libros_address)
	message = b'Hora'
	clientes = []
	try:
		sent = sock.sendto(message, server_address)
		data, server = sock.recvfrom(4096)
		horainicial = pickle.loads(data)
		print ("Hora inicial: " + str(horainicial))
		root = Tk()
		reloj = ServidorLibros(root, horainicial, sock, server_address, partner_address)
		while True:
			root.update()
			ready = select.select([sock], [], [], 0.02)
			libros = select.select([socketLibros], [], [], 0.02)
			if ready[0]:
				accion, server = sock.recvfrom(4096)
				comando = pickle.loads(accion)
				if comando[0] == 0:
					reloj.enviarhora()
					inicio = time.time()
					actualiza, server = sock.recvfrom(4096)
					actualizacion = pickle.loads(actualiza)
					if actualizacion[0] == 1:
						print("Actualizacion de hora")
						viaje = (time.time() - inicio)
						hora = cristian(actualizacion[1],viaje)
						reloj.actualizar_hora(hora)
				if comando[0] == 2:
					disp = obtenerlibros()
					print("validando libros")
					if len(disp) == 0:
						reiniciar()
						for cliente in clientes:
							socketLibros.sendto(pickle.dumps([2,"Reincio"]),cliente)


			if libros[0]:
				data, addressCliente = socketLibros.recvfrom(4096)
				if addressCliente not in clientes:
					clientes.append(addressCliente)
				solicitud = pickle.loads(data)
				if isinstance(solicitud,int):
					if solicitud == 0:
						librosdisponibles = obtenerlibros()
						if librosdisponibles:
							print("Cliente conectado: "+str(addressCliente) + " Se asignará un libro")
							asignado = random.choice(librosdisponibles)
							portada = obtenerportada(asignado)
							reloj.actualizarPortada(portada)
							cambiarDisponibilidad(asignado)
							autor = obtenerAutor(asignado)
							hora = reloj.gethora()
							h = str(hora[0])+" : "+str(hora[1])+" : "+str(hora[2])
							socketLibros.sendto(pickle.dumps([0,asignado,autor,h]),addressCliente)
							guardarPedido(addressCliente,h,asignado)
							actualizarCompanero(sock,addressCliente,h,asignado,partner_address)
						else:
							socketLibros.sendto(pickle.dumps([1,"Ocupados"]),addressCliente)

					if solicitud == 1:
						clientes.remove(addressCliente)
						print("Cliente desconectado " + str(addressCliente))
				else:
					if solicitud[0] == 3:
						cambiarDisponibilidad(solicitud[3])
						guardarPedido(solicitud[1],solicitud[2],solicitud[3])	

					if solicitud[0] == 4:
						reloj.reiniciarmet()


	finally:
	    print('Socket cerrado')
	    sock.close()