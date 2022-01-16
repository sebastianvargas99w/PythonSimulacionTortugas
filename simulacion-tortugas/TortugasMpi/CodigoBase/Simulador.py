#!/usr/bin/python3
import enum
import numpy as np	# para generar números al azar según distribución estándar
import time

from mpi4py import MPI
from Tortuga import Tortuga
from Contador import Contador 

class Simulador:
	"""
	Representa al simulador de la arribada.
	"""
	
	## VARIABLES DE CLASE
	sectores_playa = []
	marea = []
	comportamiento_tortugas = []
	tortugas = []
	transecto_berma = []
	transectos_verticales = []
	cuadrantes = []
	tics = 0			## cantidad total de tics a simular
	tic = 0				## tic actual
	conteo_tpb = 0 		## variable para el conteo basado en transecto paralelo
	conteo_tsv = 0		## variable para el conteo basado en transectos verticales
	conteo_cs = 0		## variable para el conteo basado en cuadrantes
	marea_baja = 0
	
	## MÉTODOS DE CLASE
	## EFE:Inicializa los sectores de playa con sp. 
	@classmethod
	def inicializar_playa(cls, sp):
		cls.sectores_playa = sp
		#print("playa:",cls.sectores_playa)
		return
	
	## EFE: Inicializa los datos de la marea con la posición i de la lista mareas.
	@classmethod
	def inicializar_marea(cls, mareas, i):
		cls.marea = mareas[i]
		#print("marea: ",marea)
		return

	'''
	Efe: Indica la cantidad total que necesita para llegar de la marea actual a la que debe llegar
	Req: Dos valores, el de marea baja y alta.
	Mod: N/A
	''' 
	@classmethod
	def cambio_marea(cls, val1, val2):
		return ((val1 - val2)/ float(cls.tics)) * -1


	## EFE: Inicializa la arribada con el comportamiento de las tortugas y la cantidad 
	## indicada por nt de tortugas a simular.
	@classmethod
	def inicializar_arribada(cls, comportamiento, nt):
		cls.comportamiento_tortugas = comportamiento
		#cls.tortugas = Tortuga.crear_lista_tortugas(nt) # falta el comportamiento
		return

	## EFE: Inicializa el transecto paralelo a la berma.
	@classmethod
	def inicializar_transecto_berma(cls, tb):
		cls.transecto_berma = tb
		#print("berma: ",transecto_berma)
		return
	
	## EFE: Inicializa los transectos verticales.
	@classmethod
	def inicializar_transectos_verticales(cls, tsv):	
		cls.transectos_verticales = cls.cambiar_formato_archivo_tsv(tsv)
		#print("transectos verticales: ",transectos_verticales)
		return
	
	## EFE: Inicializa los cuadrantes.
	@classmethod
	def inicializar_cuadrantes(cls, cs):
		cls.cuadrantes = cs
		#print("cuadrantes", cuadrantes)
		return

	@classmethod
	def definir_aparicion_tortugas(cls,u,s, tics, num_tortugas):
		aparicion_tortugas = [0]*tics
		for i in range (num_tortugas):
			posicion = int(np.random.logistic(s,u) + tics/2)
			# print("Posicion: ", posicion)
			# print("Aparicion posicion: ", aparicion_tortugas[posicion])
			# print("Aparicion: ", aparicion_tortugas[posicion]+1)
			aparicion_tortugas[posicion] = aparicion_tortugas[posicion]+1
		return aparicion_tortugas

	@classmethod
	def cambiar_formato_archivo_tsv(cls,transectos_verticales):
		archivo_cambiado = []
		archivo_cambiado = tuple(transectos_verticales[0:len(transectos_verticales)])
		for i in range(1,len(archivo_cambiado),1):
			archivo_cambiado[i].append(0)
			archivo_cambiado[i][3] = archivo_cambiado[i][2]
			archivo_cambiado[i][2] = archivo_cambiado[i][0]+2
		return archivo_cambiado

	#reinicia variables como contadores para poder volver a ejecutar el metodo simular
	@classmethod
	def limpiar_variables(cls):
		cls.conteo_cs = 0
		cls.conteo_tpb = 0
		cls.conteo_tsv = 0
		cls.tic = 0

	@classmethod
	def simular(cls, numero_experimento,num_tortugas, procesos_sector):
		pid = MPI.COMM_WORLD.rank
		comm = MPI.COMM_WORLD
		aparicion_tortugas = []
		cls.tic = 0
		#define en que tics hay que agregar tortugas, tambien cuantas
		if pid == 0:
			aparicion_tortugas = cls.definir_aparicion_tortugas(cls.comportamiento_tortugas[0][8],0,int(cls.marea[0][2]),num_tortugas)
		#comparte todas las variables necesarias, arreglos para la aparicion de tortugas y archivos
		aparicion_tortugas, cls.sectores_playa, cls.marea, cls.comportamiento_tortugas, cls.transecto_berma, cls.transectos_verticales, cls.cuadrantes = comm.bcast((aparicion_tortugas, cls.sectores_playa, cls.marea, cls.comportamiento_tortugas, cls.transecto_berma, cls.transectos_verticales, cls.cuadrantes),0)
  
		#tics indica la cantidad de minutos que dura el experimento, se lee del archivo marea
		cls.tics = int(cls.marea[0][2])
  
		#inicializacion de listas
		tortugas = []
		tortugas_cuadrantes = []
		tortugas_t_verticales = []
  
		

		contar_cuadrante = 0
		contar_vertical = 0
		#cada iteracion es un mimnuto del experimento
		# Chequea cual es el valor correspondiente a la marea baja segun el .csv
		marea_baja = cls.marea[numero_experimento][0] if (cls.marea[numero_experimento][0] < cls.marea[numero_experimento][1]) else  cls.marea[numero_experimento][1]

		# Se le pasa por parametro los elementos que estan en la lista marea, para que haga el cambio de marea necesario
		cambio_marea = cls.cambio_marea(cls.marea[numero_experimento][0], cls.marea[numero_experimento][1])
		marea_actual = cls.marea[numero_experimento][0] # Esta la forma correcta de calcular marea_actual
		marea_media = (cls.marea[numero_experimento][0]+cls.marea[numero_experimento][1])/2
  
		#el primer parametro es la marea alta, es importante porque puede que usemos la formula despues
		if pid == 0:
			contador_berma = Contador(int(marea_actual+cambio_marea*cls.tics), cls.transecto_berma[1][1], cls.transecto_berma[0][1],cls.transecto_berma[0][2])

		# Inicializa funciones de Tortuga necesarias antes de hacer la simuacion
		Tortuga.inicializar_diccionarios(cls.comportamiento_tortugas) # Inicializan los diccionarios antes de que aparezcan las tortugas

		#indica cuanto hay que cambiar la marea en cada tic
		for cls.tic in range (cls.tics):
    
			#crea las listas de tortugas
			if pid != 0:
				#distribuye las tortuga en partes iguales para que sean agregadas a las listas (no incluye restante)
				tortugas_nuevas,tortugas_cuadrantes_nuevas,tortugas_t_verticales_nuevas = Tortuga.crea_lista_tortugas(aparicion_tortugas[cls.tic]//comm.size,cls.cuadrantes,cls.transectos_verticales,marea_baja,marea_actual)
			else:
				#parametro que indica cuantas tortugas tiene que agregar el proceso 0, incluye el restante al divir las tortugas entre procesos
				#el restante es el segundo sumando (usa el modulo)
				#print("arreglo de aparicion tortugas:",aparicion_tortugas)
				num_tortugas_agregar = (aparicion_tortugas[cls.tic]//comm.size)+ (aparicion_tortugas[cls.tic] % comm.size)
				#if num_tortugas_agregar != 0:
					#print("params",num_tortugas_agregar,cls.cuadrantes,cls.transectos_verticales,marea_baja,marea_actual)
				tortugas_nuevas,tortugas_cuadrantes_nuevas,tortugas_t_verticales_nuevas = Tortuga.crea_lista_tortugas(num_tortugas_agregar,cls.cuadrantes,cls.transectos_verticales,marea_baja,marea_actual)
				
   
			#comunica los arreglos a otros procesos
			tmp = comm.allreduce([tortugas_nuevas,tortugas_cuadrantes_nuevas,tortugas_t_verticales_nuevas],MPI.SUM)
   
			#concatena las listas del reduce
			for i in range (0,comm.size*3,3):
				tortugas += tmp[i]
				tortugas_cuadrantes += tmp[i+1]
				tortugas_t_verticales += tmp[i+2]
			#termina de crear la lista de tortugas
   
   

			'''inicia seccion de conteo'''

			##conteo del transecto vertical

			if contar_vertical == cls.transectos_verticales[0][1]-1:
				contar_vertical = 0
				#lleva la cuenta de los transectos verticales
				sub_arreglo_tortugas = []
				conteo = 0
				#le asigna un subarreglo a cada proceso para que cuente las tortugas 
				#esto es un solo conteo, hay que pasarlo al for de los tics para que cuenta en cada tic
				if pid == 0:
					#print("contador vertical en tic: ",cls.tic)
					#toma en cuenta el restante para el proceso 0
					sub_arreglo_tortugas = tortugas_t_verticales[0:len(tortugas_t_verticales)//comm.size]

					#tamaño del arreglo estante
					restante = comm.size*(len(tortugas_t_verticales)//comm.size)

					#suma el arreglo restante
					sub_arreglo_tortugas += tortugas_t_verticales[restante:len(tortugas_t_verticales)]

					#cuentas las tortugas del arreglo
					conteo = Contador.contar_area(sub_arreglo_tortugas,cls.transectos_verticales)
					#print("pid: ",pid," conteo: ", cls.conteo_tsv," len: ",len(sub_arreglo_tortugas))
				else:
					#distribuye la longitud de los arreglos en partes iguales
					#el offset es la cantidad de tortugas que se cuentas
					offset = len(tortugas_t_verticales)//comm.size

					#posicion inicial del arreglo original donde se empiezan a contar las tortugas
					inicial =pid*offset

					#asigna el subarreglo
					sub_arreglo_tortugas = tortugas_t_verticales[inicial:inicial+offset]
					conteo = Contador.contar_area(sub_arreglo_tortugas,cls.transectos_verticales)
					#print("pid: ",pid," conteo: ", cls.conteo_tsv," len: ",len(sub_arreglo_tortugas))
				
				suma_conteos_vertical = comm.allreduce(conteo, MPI.SUM)
				cls.conteo_tsv +=suma_conteos_vertical
			else:
				contar_vertical+=1
			##conteo de cuadrantes
   
			#usa la misma logica que el conteo por transecto vertical pero con otras variables
			if contar_cuadrante == cls.cuadrantes[0][1]-1:
				contar_cuadrante = 0
				conteo = 0
				sub_arreglo_tortugas = []
				if pid == 0:
					#print("contador cuadrante en tic: ",cls.tic)
					sub_arreglo_tortugas = tortugas_cuadrantes[0:len(tortugas_cuadrantes)//comm.size]
					restante = comm.size*(len(tortugas_cuadrantes)//comm.size)
					sub_arreglo_tortugas += tortugas_cuadrantes[restante:len(tortugas_cuadrantes)]
					conteo = Contador.contar_area(sub_arreglo_tortugas,cls.cuadrantes)
				else:
					offset = len(tortugas_cuadrantes)//comm.size
					inicial =pid*offset
					sub_arreglo_tortugas = tortugas_cuadrantes[inicial:inicial+offset]
					conteo = Contador.contar_area(sub_arreglo_tortugas,cls.cuadrantes)
				suma_conteo_cuadrante = comm.allreduce(conteo, MPI.SUM)
				cls.conteo_cs += suma_conteo_cuadrante
				#if pid ==0:
					#print("cuadrantes  parallel: ",cls.conteo_cs)
			else:    
				contar_cuadrante +=1	
			##conteo del transecto paralelo

			#avanzar al contador (si no tiene que avanzar aumenta el contador o cambia de estado)
			#como es un proceso por sector entonces solo lo hace el proceso 0
			if pid ==0:
				contador_berma.avanzar()
				if contador_berma.obt_estado() ==  Contador.EstadoContador.contar:
					cls.conteo_tpb += contador_berma.contar_transecto_paralelo(tortugas,tortugas_cuadrantes,tortugas_t_verticales,cls.transecto_berma,round(marea_media))
			####seccion de cambio de estado, integrar al resto NO OLVIDAR
			# Aca se le cambia el estado a las tortugas y se avanzan en la posicion
			comm.barrier()
   
			if pid ==0:
				Tortuga.cambiar_estado(tortugas,tortugas_cuadrantes,tortugas_t_verticales)
			tortugas,tortugas_cuadrantes,tortugas_t_verticales = comm.bcast((tortugas,tortugas_cuadrantes,tortugas_t_verticales),0)
			marea_actual += cambio_marea
   
			##fin del if de tics
   
		if pid ==0:
			print("len: ",len(tortugas)+len(tortugas_cuadrantes)+len(tortugas_t_verticales))
			print("len tortugas: ", len(tortugas))
			print("len cuadrantes: ",len(tortugas_cuadrantes))
			print("len transecto vertical: ",len(tortugas_t_verticales))
	
			print("cuadrante : ",cls.conteo_cs)
			print("transecto paralelo: ",cls.conteo_tpb)
			print("transecto verticales : ",cls.conteo_tsv)

			print("Tortugas desactivadas por anidar en lugares ocupados: ", len(Tortuga.dict_tortugas_anindando))
   
   
		# Llamado a los mecanismos de conteo:
		resultado_paralelo = cls.obtener_tpb(cls.conteo_tpb, cls.transecto_berma[0][1], cls.tics//cls.transecto_berma[0][1])	
		resultado_vertical = cls.obtener_tvb(cls.tics, marea_media ,(cls.transectos_verticales[1][2] - cls.transectos_verticales[1][0]) + 2, cls.tics//cls.transectos_verticales[0][1], cls.conteo_tsv)	
		resultado_cuadrante = cls.obtener_conteo_cuadrante(cls.conteo_cs,marea_media, cls.tics, cls.tics//cls.cuadrantes[0][1])

		cls.limpiar_variables()
		return resultado_cuadrante,resultado_vertical,resultado_paralelo,num_tortugas,len(Tortuga.dict_tortugas_anindando)

	
	'''
	Efe: Obtiene el conteo de tortugas en los transectos paralelos
	Req: Ninugno de las variables puede ser 0 o menor
	Mod: N/A
	'''
	@classmethod
	def obtener_tpb	(cls, conteo_tpb, minutos, muestreos):
		print("conteo: ", conteo_tpb, "minutos: ", minutos, "Muestreos: ", muestreos)
		formula = ((conteo_tpb//4) * minutos) / (4.2 * muestreos)
		#print("Resultado tpb: ", formula)
		return formula

	'''
	Efe: Obtiene el conteo de tortugas en los transectos verticales
	Req: duracion_minutos, marea_media ,ancho_transecto, muestreos, conteo_tvb
	Mod: N/A
	'''
	@classmethod
	def obtener_tvb(cls, duracion_minutos, marea_media ,ancho_transecto, muestreos, conteo_tvb):
		promedio_minutos = 64.8		
		sumatoria_longitudes = 0
		area = (100 - (marea_media + cls.sectores_playa[0][2]) ) * 1500

		# Obtiene sumatoria de longitudes
		for x in range(1, len(cls.transectos_verticales)):
			sumatoria_longitudes += cls.transectos_verticales[x][3] - cls.transectos_verticales[x][1]
		formula =  ((area * duracion_minutos) / (2* ancho_transecto * muestreos * sumatoria_longitudes)) * (conteo_tvb/promedio_minutos)
		#print("Resultado tvb: ", formula)
		return formula

	'''
	Efe: Obtiene el conteo de tortugas en los cuadrantes
	Req: sumatoria_tortugas, marea_media , duracion, muestreos
	Mod: N/A
	'''
	@classmethod
	def obtener_conteo_cuadrante(cls, sumatoria_tortugas, marea_media , duracion, muestreos):
		area_cuadrante = ((cls.cuadrantes[1][3] - cls.cuadrantes[1][1]) * (cls.cuadrantes[1][2] - cls.cuadrantes[1][0]))* len(cls.cuadrantes) -1
		area_observacion = (100 - (marea_media + cls.sectores_playa[0][2]) ) * 1500				
		formula =  (sumatoria_tortugas * 1.25 * (area_cuadrante/area_observacion) * duracion) / 1.08 * muestreos
		#print("Resultado conteo cuadrantes: ", formula)
		return formula


	
	## DE ESTA CLASE SIMULADOR SÓLO EXISTIRÍA UNA INSTANCIA (SINGLETON).
	## POR LO QUE NO SE INCLUYEN MÉTODOS DE INSTANCIA, SÓLO MÉTODOS DE CLASE.

		
	