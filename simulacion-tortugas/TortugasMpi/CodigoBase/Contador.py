#!/usr/bin/python3
import enum
import numpy as np	# para generar números al azar según distribución estándar
import json			# para crear una hilera json en toJSON()
import random

class Contador:
	"""
	Representa una Contador con id, velocidad y posicion.
	"""
	
	## VARIABLES DE CLASE
	id = 0 		## OJO variable static de clase para generar ids de Contadores
	
	## MÉTODOS DE CLASE
	""" metodo de clase que genera N Contadors """
	''' @classmethod
	def crea_lista_Contadores(cls,N,marea_alta, longitud_berma):
		contadores = []
		for i in range(N):
			t_n = Contador(marea_alta, longitud_berma)
			contadores.append(t_n)
		return contadores '''
	
	class EstadoContador(enum.Enum):
		contar = 0
		esperar = 1

	## MÉTODOS DE INSTANCIA
	
	## EFE: crea una Contador inicializada al azar.
	def __init__(self,marea_alta, longitud_berma, tiempo_cambiar_estado,vision):
		self.id = Contador.id
		Contador.id += 1
		self.velocidad = 100
		self.posicion = 0,marea_alta ## OJO: así se crea un par ordenado, un tuple de dos valores
		self.estado = Contador.EstadoContador.esperar
		self.longitud_berma = longitud_berma#para que el contador sepa hasta donde llegar
		self.tiempo_cambiar_estado = tiempo_cambiar_estado -1
		self.contador_estado = 0
		self.vision = vision
		return
	
	## EFE: retorna una hilera en formato JSON que representa a la Contador
	def toJSON(self):
		# (type(self).__name__ retorna como hilera el nombre de la clase de self
		# se le pasa un tuple con el nombre de la clase y los valores de los atributos de self
		return json.dumps((type(self).__name__, self.id, self.velocidad, self.posicion))
	
	def obt_id(self):
		return self.id
		
	def obt_velocidad(self):
		return self.velocidad
	
	def obt_posicion(self):
		return self.posicion
		
	def asg_velocidad(self, vn):
		self.velocidad = vn
		return
		
	def asg_posicion(self, pn):
		self.posicion = pn
		return

	def obt_estado(self):
		return self.estado

	def cambiar_estado(self):
		if self.contador_estado == self.tiempo_cambiar_estado:
			if self.estado == Contador.EstadoContador.esperar:
				self.estado = Contador.EstadoContador.contar
			else:
				self.estado = Contador.EstadoContador.esperar
			self.contador_estado = 0
		else:
			self.contador_estado+= 1
		
	## EFE: avanza la Contador de acuerdo con su estado, si es necesario el contador se devuelve
	def avanzar(self):
		if self.estado == Contador.EstadoContador.contar :
			proximo_x = self.posicion[0] + self.obt_velocidad()

			#revisa los limites de transecto paralelo
			if proximo_x>self.longitud_berma or proximo_x<0 :

				#multiplica por -1 para que se devuelva y vea al lado que esta caminando
				self.velocidad = self.velocidad*-1
				self.vision = self.vision*-1

			#cambia posicion (avanza)
			self.posicion = (self.posicion[0]+self.obt_velocidad(),self.posicion[1])
		self.cambiar_estado()
		#print("estado: ",self.estado,self.contador_estado, " posicion: ", self.posicion)

		return

	def generar_sector_paralelo(self,transecto_paralelo,marea_media,posicion,vision):
		#print(self.posicion,self.vision)

		#inicializa la matriz con el secto
		sector = []
		sector.append([])
		sector.append([])

		x_izquierda = 0
		x_derecha = 0

		#ve para la derecha
		if self.vision >= 0:
			x_izquierda = self.posicion[0]
			x_derecha = self.posicion[0]+self.vision
		#ve para la izquierda
		else:
			x_izquierda = self.posicion[0]+self.vision		
			x_derecha = self.posicion[0]

		#llena la matriz con los limites del sector
		sector[1].append(x_izquierda)
		sector[1].append(marea_media)
  
		sector[1].append(x_derecha)
		sector[1].append(marea_media + transecto_paralelo[0][1])
		#print("sector",sector)#ancho de la bermas  
		return sector

	def contar_transecto_paralelo(self,tortugas,tortugas_cuadrantes,tortugas_t_verticales,transecto_paralelo,marea_media):
		conteo = 0
  
		#hace una matriz(para mantener el formato del metodo contar_area) con el area que se necesita revisar
		sector = self.generar_sector_paralelo(transecto_paralelo,marea_media,self.posicion,self.vision)

		#cuenta cada arreglo y lo almacena en conteo
		conteo += self.contar_area(tortugas,sector)
		conteo += self.contar_area(tortugas_cuadrantes,sector)
		conteo += self.contar_area(tortugas_t_verticales,sector)
		return conteo

	#cuenta las tortugas de un sector (el param sector normalmente es un archivo con cierto formato)
	@classmethod
	def contar_area(self, tortugas, sector):
     
		#indica cuantas tortugas han sido contadas
		tortugas_contadas = 0
		#recorre la lista de tortugas
		for i in range (len(tortugas)):
			# No cuenta las tortugas que estan desactivadas
			if tortugas[i].estado.value != -1:
    
				#obtiene la posicion de la tortuga
				posicion = tortugas[i].obt_posicion()
				j = 1
				seguir = True
				#print(posicion,tortugas,sector)
				while j < len(sector) and seguir==True:
					#verifica que la tortugas este en el sector
					if posicion[0] >= sector[j][0] and posicion[1]>= sector[j][1] and posicion[0] <= sector[j][2] and posicion[1]<=sector[j][3]:
						
						#si encuentra la tortuga deja de interar para seguir con la otra y suma el contador
						seguir = False
						tortugas_contadas+=1
					j+=1	
				
		return tortugas_contadas