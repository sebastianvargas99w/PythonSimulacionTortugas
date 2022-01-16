#!/usr/bin/python3

import sys
import csv
from enum import Enum
from mpi4py import MPI
from Tortuga import Tortuga
from Contador import Contador
from Simulador import Simulador

#matriz_comportamiento_tortuga = [[0 for x in range(9)] for y in range(2)] 

## Para lectura de archivos de texto en python ver:
## https://www.pythonforbeginners.com/files/reading-and-writing-files-in-python

## Para leer archivos csv con numeros con python ver:
## https://pythonprogramming.net/reading-csv-files-python-3/

## Para manejo de excepciones en python ver:
## https://docs.python.org/3/library/exceptions.html

## Tipo enumerado para los dos tipos de numeros que se pueden leer
class Tipos_numeros(Enum):
	int = 0
	float = 1
 
tiempo_pared_ant = 1

## EFE: lee un archivo csv con numeros separados por coma y retorna una lista 
## de listas de numeros de tipo tn.
def lee_numeros_csv(archivo,tn):
	lista = []
	read_csv = csv.reader(archivo, delimiter=',')
	for row in read_csv:
		sublista = []
		for n in row:
			try:
				if (tn == Tipos_numeros.int):
					sublista.append(int(n))
				else: 
					sublista.append(float(n))
			except ValueError as error_de_valor:
				print("Error de tipo de valor: {0}".format(error_de_valor))
		lista.append(sublista)
	return lista

def leer_archivos_simulador():
	try:
		with open("..\Archivos\\terreno.csv") as terreno_csv:
			Simulador.inicializar_playa(lee_numeros_csv(terreno_csv,Tipos_numeros.float))
	except OSError as oserror:
		print("Error de entrada-salida de archivos: {0}".format(oserror))
  	##Ejemplo de cargar marea, hay que cambiar el ultimo parametro dependiendo del experimento
	try:
		with open("..\Archivos\\marea.csv") as marea:
			Simulador.marea = lee_numeros_csv(marea,Tipos_numeros.float)
	except OSError as oserror:
		print("Error de entrada-salida de archivos: {0}".format(oserror))
	try:
		with open("..\Archivos\\transecto_paralelo_berma.csv") as berma:
			Simulador.inicializar_transecto_berma(lee_numeros_csv(berma,Tipos_numeros.int))
	except OSError as oserror:
		print("Error de entrada-salida de archivos: {0}".format(oserror))
	try:
		with open("..\Archivos\\transectos_verticales.csv") as vertical:
			Simulador.inicializar_transectos_verticales(lee_numeros_csv(vertical,Tipos_numeros.int))
	except OSError as oserror:
		print("Error de entrada-salida de archivos: {0}".format(oserror))
	try:
		with open("..\Archivos\\cuadrantes.csv") as cuadrantes:
			Simulador.inicializar_cuadrantes(lee_numeros_csv(cuadrantes,Tipos_numeros.int))
	except OSError as oserror:
		print("Error de entrada-salida de archivos: {0}".format(oserror))	
	return
    

'''
Efe: Genera una lista con los resultados
Req: El tiempo pared del experimento, el numero de procesos que se estan usando y el experimento
Mod: N/A
Param: Direccion IP del nodo
''' 

def generar_archivo_resultado(tiempo_pared,num_proces, experimento):
	# Se guarda los resutlados en el primer experimento
	global tiempo_pared_ant
	lista_valores = []
	lista_valores.append(num_proces)
	lista_valores.append(tiempo_pared)
	aceleracion = 0
	eficiencia = 0
	resultado_experimento1 = []
	resultado_experimento2 = []
	resultado_experimento3 = []

	# Obtiene la aceleracion y eficiencia
	if tiempo_pared_ant == 1:	
		aceleracion = tiempo_pared // tiempo_pared
		eficiencia = aceleracion
	else:
		aceleracion = tiempo_pared_ant / tiempo_pared 
		eficiencia = aceleracion / num_proces
	
	# Guarda los resultados obtenidos
	lista_valores.append(aceleracion)
	lista_valores.append(eficiencia)

	# Guarda la informacion para el primer experimento
	if experimento == 1:
		resultado_experimento1.append(lista_valores)

		# Se actualiza el valor del tiempo pared anterior
		tiempo_pared_ant = tiempo_pared
		
		# Devuelve la lista con los resultados si el tamanno de la lista es igual a tres
		if len(resultado_experimento1) == 3:
			tiempo_pared_ant = 0 # Reinicia el valor de la variable
			lista_valores.clear() # Limpia la lista
			return resultado_experimento1
	
	# Guarda la informacion para el segundo experimento
	elif experimento == 2:
		resultado_experimento2.append(lista_valores)

		# Se actualiza el valor del tiempo pared anterior
		tiempo_pared_ant = tiempo_pared
		
		# Devuelve la lista con los resultados si el tamanno de la lista es igual a tres
		if len(resultado_experimento2) == 3:
			tiempo_pared_ant = 0 # Reinicia el valor de la variable
			lista_valores.clear() # Limpia la lista
			return resultado_experimento2
	
	# Guarda la informacion para el primer experimento
	elif experimento == 3:
		resultado_experimento3.append(lista_valores)

		# Se actualiza el valor del tiempo pared anterior
		tiempo_pared_ant = tiempo_pared
		
		# Devuelve la lista con los resultados si el tamanno de la lista es igual a tres
		if len(resultado_experimento3) == 3:
			tiempo_pared_ant = 0 # Reinicia el valor de la variable
			lista_valores.clear() # Limpia la lista
			return resultado_experimento3
	


def main():
	comportamiento = []
	experimento = []
	comm = MPI.COMM_WORLD
	pid = MPI.COMM_WORLD.rank
	## OJO: el archivo esta en una carpeta "archivos"
	##lectura de archivo comportamiento y experimentos
	##solo el proceso 0 lee los archivos porque si se ejecutan muchos procesos son muchas
	##lecturas para un solo disco duro (suponiendo que se usa una computadora de escritorio)
	if pid == 0:
		try:
			with open("..\Archivos\comportamiento_tortugas.csv") as ct_csv:
				comportamiento = lee_numeros_csv(ct_csv,Tipos_numeros.float)
			#print("comportamiento: ",comportamiento)
		except OSError as oserror:
			print("Error de entrada-salida de archivos: {0}".format(oserror))
		
		try:
			with open("..\Archivos\\experimentos.csv") as experimento:
				experimento = lee_numeros_csv(experimento,Tipos_numeros.int)
			#print("experimento: ",experimento)
		except OSError as oserror:
			print("Error de entrada-salida de archivos: {0}".format(oserror))
		leer_archivos_simulador()
  
	comportamiento, experimento = comm.bcast((comportamiento,experimento),0)
	CANTIDAD_EXPERIMENTOS = experimento[0][1]+1
	##NO BORRAR
	#comentado para hacer pruebas y que no duren mucho
	# ## i es el numero actual de experimento 
	
	#almacena resultado con los tiempos
	resultados = []
 
	#para cada experimento, son 3
	for z in range (len(experimento)-1):

		for i in range (0,CANTIDAD_EXPERIMENTOS,1):
			
			## j es la n-esima vez que se ejecuta un mismo experimento
			for j in range(0,experimento[i][0]-7):
				inicio = MPI.Wtime()
				Simulador.inicializar_arribada(comportamiento,experimento[z][2])
				##arreglar el ultimo parametros(procesos por nodo)
				final = inicio - MPI.Wtime()
				#salida = Simulador.simular(i,experimento[z][2],experimento[z][3])
				salida = Simulador.simular(i,10,experimento[z][3])
				print("Estimado de tortugas en cuadrante: ", salida[0])
				print("Estimado de tortugas en transecto vertical: ", salida[1])
				print("Estimado de tortugas en transecto paralelo: ", salida[2])
				print("Numero real de tortugas: ", salida[3])
				print("Total de tortugas que anidaron: ", salida[4])
				resultados.append(generar_archivo_resultado(final,comm.size,j))
				print("termino la ejecucion: ", j, " del experimento: ", z)
    comm.barrier()
	if pid==0:
		print("resultados",resultados)
    

 
	#seccion para hacer pruebas BORRAR AL ENTREGAR PROYECTO
	# num_tortugas = 7000
	# Simulador.inicializar_arribada(comportamiento,experimento[0][2])
	# Simulador.simular(0,num_tortugas,experimento[0][3])
 
	return

main()