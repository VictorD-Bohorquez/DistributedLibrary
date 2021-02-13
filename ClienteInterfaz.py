from  tkinter import *
import time
import pickle

class ClienteInterfaz:
	def __init__(self,master, s, server):
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.cerrar_sesion)
		self.master.geometry("460x210")
		self.master.title('Petición de Libros')
		self.master.configure(background='black')
		self.digi=Label(master,text="Sin solicitudes",font="times 12 bold",fg="red",background="black")
		self.digi.grid(row=1,column=1)
		self.pedir = Button(master, text="Solicitar Libro", command=self.pedir, bg="#0d7377")
		self.pedir.place(x= 185, y= 160)
		self.libro = Text(master, bg="white", height= 4, width = 50)
		self.libro.grid(row = 0, column = 1, pady=25,padx=25)
		self.socket = s
		self.servidor = server

	def pedir(self):
		sent = self.socket.sendto(pickle.dumps(0), self.servidor)

	def cerrar_sesion(self):
		sent = self.socket.sendto(pickle.dumps(1), self.servidor)
		self.master.destroy()

	def actualizalibro(self,libro,autor,h):
		self.libro.delete(1.0,"end")
		self.libro.delete(2.0,"end")
		self.libro.insert(1.0,("Libro: "+libro+"\n"))
		self.libro.insert(2.0,("Autor: "+autor))
		self.digi.config(text = "Solicitado a las "+ h)

	def limpialibro(self):
		self.libro.delete(1.0,"end")
		self.libro.delete(2.0,"end")
		self.digi.config(text = "No disponible intente en un momento")

	def reinicio(self):
		self.libro.delete(1.0,"end")
		self.libro.delete(2.0,"end")
		self.digi.config(text = "Aplicacion reiniciada")