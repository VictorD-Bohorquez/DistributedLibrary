from  tkinter import *
import time
import pickle
from PIL import ImageTk,Image
import mysql.connector

class ServidorLibros:
	def __init__(self,master, h, s, utc,comp):
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.cerrar_sesion)
		self.master.geometry("460x470")
		self.master.title('Reloj de Servidor')
		self.master.configure(background='black')
		self.hora_texto = Label(master, fg="green", font=("times",50,"bold"), background="black")
		self.hora_texto.grid(row=2,column=1,pady=25,padx=100)
		self.digi=Label(master,text=" Hora Actual",font="times 24 bold",fg="red",background="black")
		self.digi.grid(row=1,column=1)
		self.modificar = Button(master, text="Modificar", command=self.modificar, bg="#0d7377")
		self.modificar.place(x= 100, y= 410)
		self.reiniciar = Button(master, text="Reiniciar", command=self.reiniciar, bg="#0d7377")
		self.reiniciar.place(x=300, y =410)
		self.imagen = Canvas(master,width = 150, height =180)
		self.imagen.grid(row = 0, column = 1, pady=25,padx=100)
		self.hour = h
		self.proceso = 0
		self.socket = s
		self.sutc = utc
		self.compa = comp
		self.iniciar()

	def sumar(slef , h):
		h[2]+=1
		if h[2]>= 60:
			h[1]+=1
			h[2]=0
			if h[1]>= 60:
				h[1]=0
				h[0]+=1
				if h[0]>=24:
					h[0]= 0
		return h

	def iniciar(self):
	    hora= str(self.hour[0])+":"+str(self.hour[1])+":"+str(self.hour[2])
	    hora = time.strptime(hora,"%H:%M:%S")
	    self.hora_texto.config(text = time.strftime("%H:%M:%S",hora))
	    self.hour = self.sumar(self.hour)
	    self.proceso = self.hora_texto.after(int(1000*self.hour[3]), self.iniciar)

	def cambiar_hora(self):
		hora = int(self.hr.get())
		minuto = int(self.min.get())
		seg = int(self.seg.get())
		if hora <24 and hora>=0 and minuto <60 and minuto>=0 and seg<60 and seg>=0:
			if self.vel.get() == "" or self.vel.get() == 1:
				h= [hora,minuto,seg,1]
			else:
				h= [hora,minuto,seg,float(self.vel.get())]
			self.hour = h
			self.ventana_mod.destroy()
			self.iniciar()
		else:
			self.error()

	def actualizarPortada(self, ruta):
		i =Image.open(ruta)
		i = i.convert("RGB")
		newsize = (150, 180)
		i = i.resize(newsize) 
		img = ImageTk.PhotoImage(i)
		self.im = img
		self.imagen.create_image((0,0),image=self.im,anchor='nw')
		self.imagen.update()

	def error(self):
		self.resultado.config(bg="#b83b5e", text="Hora inválida")
		self.master.after(1500,self.limpiar)

	def limpiar(self):
		self.resultado.config(bg="#212121",text="")

	def cerrar_ventana(self):
		self.ventana_mod.destroy()
		self.iniciar()

	def cerrar_sesion(self):
		sent = self.socket.sendto(pickle.dumps([5,self.hour]), self.sutc)
		self.master.destroy()

	def modificar(self):
		self.hora_texto.after_cancel(self.proceso)
		self.ventana_mod = Toplevel(self.master)
		self.ventana_mod.geometry("400x150")
		self.ventana_mod.title('Cambiar Hora')
		self.ventana_mod.config(bg="#212121")
		self.ventana_mod.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)
		self.texto =  Label(self.ventana_mod,text="Hora                         Minuto                           Seg                           Vel",bg="#212121",fg="#FFFFFF")
		self.texto.pack()
		self.hr= Entry(self.ventana_mod,width=10,bg="#32e0c4")
		self.hr.place(x=20,y=40)
		self.min = Entry(self.ventana_mod,width=10,bg="#32e0c4")
		self.min.place(x=120,y=40)
		self.seg = Entry(self.ventana_mod,width=10,bg="#32e0c4")
		self.seg.place(x=220,y=40)
		self.vel = Entry(self.ventana_mod,width=10,bg="#32e0c4")
		self.vel.place(x=320,y=40)
		self.resultado = Label(self.ventana_mod,text="",bg="#212121",fg="#FFFFFF")
		self.resultado.config(width=22)
		self.resultado.place(x=80,y=80)
		self.guardar= Button(self.ventana_mod, text="Guardar", command=self.cambiar_hora, bg="#0d7377")
		self.guardar.place(x= 175, y= 100)
		self.ventana_mod.focus_set()
		self.master.wait_window(self.ventana_mod)

	def actualizar_hora(self , h):
		self.hora_texto.after_cancel(self.proceso)
		self.hour = h
		self.iniciar()

	def enviarhora(self):
		sent = self.socket.sendto(pickle.dumps([0,self.hour]), self.sutc)

	def gethora(self):
		return self.hour

	def conexion(self):
		conexion=mysql.connector.connect(host="localhost", user="root", passwd="blackmaria", database="libros")
		return conexion

	def obtenerid(self,libro):
		con = self.conexion()
		sql = """select idLibro from Libro where nombre = %s"""
		cursor = con.cursor(prepared=True)
		cursor.execute(sql,(libro,))
		idlib = cursor.fetchone()
		con.close()
		return idlib[0]


	def cambiarDisponibilidad(self,libro):
		con = self.conexion()
		idlib = self.obtenerid(libro)
		sql = """update Libro set disponibilidad = 'S' where idLibro = %s"""
		cursor = con.cursor(prepared=True)
		cursor.execute(sql,(idlib,))
		con.commit()
		con.close()

	def reiniciar(self):
		con = self.conexion()
		cursor=con.cursor()
		cursor.execute("select nombre from libro")
		libros = []
		for libro in cursor:
			libros.append(libro[0])
		con.close()
		print (libros)
		for lib in libros:
			self.cambiarDisponibilidad(lib)
		self.socket.sendto(pickle.dumps([4,"ReincioManual"]),self.compa)

	def reiniciarmet(self):
		con = self.conexion()
		cursor=con.cursor()
		cursor.execute("select nombre from libro")
		libros = []
		for libro in cursor:
			libros.append(libro[0])
		con.close()
		print (libros)
		for lib in libros:
			self.cambiarDisponibilidad(lib)

