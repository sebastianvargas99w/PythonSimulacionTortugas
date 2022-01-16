#!/usr/bin/python3
import enum
# from enum import Enum 
import numpy as np	# para generar números al azar según distribución estándar
import json			# para crear una hilera json en toJSON()
import random
from mpi4py import MPI

class Tortuga:
	"""
	Representa una tortuga con id, velocidad y posicion.
	"""

	comm = MPI.COMM_WORLD
	
	## VARIABLES DE CLASE
	id = 0 		## OJO variable static de clase para generar ids de lista
	
	# Diccionarios: 
	dict_proba_desactivar = {} 
	dict_proba_cambio_estado = {}
	dict_tortuga_estado = {}
	dict_tortugas_anindando = {}
	## FIN DE VARIABLES DE CLASE

	## MÉTODOS DE CLASE
	
	'''
	Efe: Llena los diccionarios de cambio de estado y desactivacion
	Req: Lista de comportamiento_tortugas donde vienen las probabilidades
	Mod: Crea una llave y el valor de la llave (estado: promedio_por_estado, desviacion standar)
	'''
	@classmethod
	def inicializar_diccionarios(cls, comportamiento_tortugas):
			# Llenado del diccionario de desactivacion
			cls.dict_proba_desactivar = dict.fromkeys([0, 1, 3], comportamiento_tortugas[0][0]) # Para obtener la proba de 0.2
			cls.dict_proba_desactivar.update(dict.fromkeys([4, 5], comportamiento_tortugas[0][4])) # Para obtener la proba de 0.01
			cls.dict_proba_desactivar.update(dict.fromkeys([2], comportamiento_tortugas[0][2])) # Para obtener la proba de 0.6
			
			# Llenado del diccionario cambio de estado
			cls.dict_proba_cambio_estado = dict.fromkeys([1], (comportamiento_tortugas[1][0], comportamiento_tortugas[1][1])) 
			cls.dict_proba_cambio_estado.update(dict.fromkeys([2], (comportamiento_tortugas[1][2], comportamiento_tortugas[1][3]))) 
			cls.dict_proba_cambio_estado.update(dict.fromkeys([3], (comportamiento_tortugas[1][4], comportamiento_tortugas[1][5]))) 
			cls.dict_proba_cambio_estado.update(dict.fromkeys([4], (comportamiento_tortugas[1][6], comportamiento_tortugas[1][7]))) 
			cls.dict_proba_cambio_estado.update(dict.fromkeys([5], (comportamiento_tortugas[1][8], comportamiento_tortugas[1][9])))

			# Llenado del diccionario cambio de estado
			cls.dict_tortuga_estado = {
				-1 : Tortuga.EstadoTortuga.desactivar,
				0 : Tortuga.EstadoTortuga.vagar,
				1 : Tortuga.EstadoTortuga.camar,
				2 : Tortuga.EstadoTortuga.excavar,
				3 : Tortuga.EstadoTortuga.poner,
				4 : Tortuga.EstadoTortuga.tapar,
				5 : Tortuga.EstadoTortuga.camuflar,
			}


	'''
	Efe: Modifica el cambio de estado de la tortuga
	Req: Listas de lista, tortugas_cuadrantes, tortugas_t_verticales
	Mod: El estado de la tortuga y el movimiento de la tortuga
	'''
	@classmethod
	def cambiar_estado(cls,tortugas,tortugas_cuadrantes,tortugas_t_verticales):
		listas_tortugas = [tortugas,tortugas_cuadrantes,tortugas_t_verticales]
		
		# Itera por cada una de las listas que se agregaron a listas_tortugas
		for lista in range(len(listas_tortugas)):
			# Se analiza lista de tortugas_nuevas
			for ite in range(len(listas_tortugas[lista])):

				# Se analizan las lista con su estado y posicion
				if listas_tortugas[lista][ite].estado.value != -1: # Solo se modifican las lista que no se desactivan
					# Desactiva las lista que terminaron de camuflar
					if listas_tortugas[lista][ite].estado == Tortuga.EstadoTortuga.camuflar and listas_tortugas[lista][ite].duracion_estado - 1 == 0:
						listas_tortugas[lista][ite].estado = Tortuga.EstadoTortuga.desactivar
					else:
						valor = random.randint(1,101)

						# Revisa si la tortuga_ite se desactiva
						if valor <= (cls.dict_proba_desactivar.get(listas_tortugas[lista][ite].estado.value)* 100):
							listas_tortugas[lista][ite].estado = Tortuga.EstadoTortuga.desactivar
						# Si el estado es vagar
						elif listas_tortugas[lista][ite].estado.value == 0:
							# Mueve las tortugas que estan en la lista, las que no se desactivan y que esta vagando
							cls.mover_tortuga(listas_tortugas[lista][ite])
							
						# Revisa si duracion_estado es 0
						# Si es 0 se cambia de estado
						if listas_tortugas[lista][ite].duracion_estado - 1 == 0 and listas_tortugas[lista][ite].estado.value != -1:
							
							#1- Cambiar de estado
							listas_tortugas[lista][ite].estado = cls.dict_tortuga_estado.get(listas_tortugas[lista][ite].estado.value + 1)
							
							# Verifica que dos tortugas no excaven y pongan huevos en el mismo lugar
							if listas_tortugas[lista][ite].estado == Tortuga.EstadoTortuga.excavar:
								if cls.dict_tortugas_anindando.get(listas_tortugas[lista][ite].posicion) == None:
									cls.dict_tortugas_anindando.update({listas_tortugas[lista][ite].posicion : listas_tortugas[lista][ite] })
									#print("Posicion de tortuga anindando: ", cls.dict_tortugas_anindando.get(listas_tortugas[lista][ite].posicion))
								else:
									listas_tortugas[lista][ite].estado = Tortuga.EstadoTortuga.desactivar
									#print("Tortuga desactivada por poner en un lugar ocupado")
							
							#2- Volver a calcular duracion segun de estado
							if listas_tortugas[lista][ite].estado != Tortuga.EstadoTortuga.desactivar:
								listas_tortugas[lista][ite].duracion_estado = round(np.random.normal(cls.dict_proba_cambio_estado.get(listas_tortugas[lista][ite].estado.value)[0] , cls.dict_proba_cambio_estado.get(listas_tortugas[lista][ite].estado.value)[1]))
						else:
							listas_tortugas[lista][ite].duracion_estado -= 1

		tortugas = listas_tortugas[0]	
		tortugas_cuadrantes = listas_tortugas[1]
		tortugas_t_verticales = listas_tortugas[2]	

		
	'''
	Efe: Modificar la posicion de la tortuga, esto se necesita para el siguiente tic
	Req: Tortuga a la que se le va a cambiar la posicion
	Mod: tortuga.posicion
	'''
	@classmethod
	def mover_tortuga(cls,tortuga):
		tortuga.posicion = (tortuga.posicion[0], tortuga.posicion[1] + tortuga.velocidad)
		return


	""" metodo de clase que genera N lista """
	@classmethod
	def crea_lista_tortugas(cls,N,cuadrantes,verticales,marea_baja, marea_actual):
		lista = []
		tortugas_cuadrantes = []
		tortugas_t_verticales = []
		cls.ultima_marea_baja = marea_baja
		
		# Agrega lista a la lista con lista del cuadrante		
		for i in range (0,N):
			#cambiar por while
			i = 1
			seguir = True
			tortuga=Tortuga(marea_baja, marea_actual)
			while i < len(cuadrantes) and seguir==True:
				if tortuga.obt_posicion()[0] >= cuadrantes[i][0] and tortuga.obt_posicion()[0] <= cuadrantes[i][2]:
					tortugas_cuadrantes.append(tortuga)
					seguir = False
				i+=1
			i = 1
			while i < len(verticales) and seguir == True:
				if tortuga.obt_posicion()[0] >= verticales[i][0] and tortuga.obt_posicion()[0] <= verticales[i][0]+2:
					tortugas_t_verticales.append(tortuga)
					seguir = False
				i+=1
			if seguir == True:
				seguir == False
				lista.append(tortuga)
		return lista,tortugas_cuadrantes,tortugas_t_verticales
	
	class EstadoTortuga(enum.Enum):
		vagar = 0
		camar = 1
		excavar = 2
		poner = 3
		tapar = 4
		camuflar = 5
		desactivar = -1		
		
	## MÉTODOS DE INSTANCIA

	## EFE: crea una tortuga inicializada al azar.
	def __init__(self, marea_baja, marea_actual):
		self.id = Tortuga.id
		Tortuga.id += 1
		self.velocidad = round(np.random.normal(7.3, 1.0))
		self.posicion = round(np.random.uniform(0, 1499)), round(np.random.uniform(marea_baja, marea_actual))
		self.estado = Tortuga.EstadoTortuga.vagar
		
		# Tiempo que la tortuga dura en un estado
		duracion = round(np.random.normal( self.dict_proba_cambio_estado.get(1)[0], self.dict_proba_cambio_estado.get(1)[1])) 
		self.duracion_estado = duracion if duracion > 0 else duracion * -1		
		return
	
	## EFE: retorna una hilera en formato JSON que representa a la tortuga
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
		
	## EFE: avanza la tortuga de acuerdo con su estado
	def avanzar(self):
		return
	
