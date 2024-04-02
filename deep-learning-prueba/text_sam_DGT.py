# Importamos las librerías necesarias

from arcgis.gis import GIS
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import os
import arcpy
from arcpy.ia import *
from datetime import datetime


# Conectamos a ArcGIS Online

gis = GIS("home")

# Accedo al servicio

idServicio = "13c0065c40984c34baae3493061646ce"

camarasTrafico = gis.content.get(idServicio).layers[0]

camarasTraficoDF = camarasTrafico.query(as_df=True)

# ¡¡IMPORTANTE INSERTA LA RUTA DEL DIRECTORIO DE TRABAJO!!ç
# Por favor crea una nueva carpeta donde se guarde la ejecución

directorioTrabajo = ''

# Check de las extensiones necesarias

arcpy.CheckOutExtension("ImageExt")
arcpy.CheckOutExtension("ImageAnalyst")

# Creo una GDB de Trabajo

arcpy.env.overwriteOutput = True

# ¡¡CAMBIA EL NOMBRE DE LA GDB SI QUIERES!!

nombreGDBSalida = 'resultados.gdb'

arcpy.management.CreateFileGDB(directorioTrabajo, nombreGDBSalida)

rutaGDB = os.path.join(directorioTrabajo, nombreGDBSalida)

arcpy.env.workspace = rutaGDB

print('GDB Creada')

# Crear la Carpeta donde se guardan las imagenes

nombreCarpetaImagenes = 'ImagenesEvaluadas'

rutaCarpetaImagenes = os.path.join(directorioTrabajo,nombreCarpetaImagenes)

os.mkdir(rutaCarpetaImagenes)

print('Directorio Imagenes Creado')

# INserta Ruta del TextSAM.dlpk

textSAM_dlpk = ""


# Configuración de la herramienta

def DetectDGT (imagenEntradaModelo, rutaDeSalida ,prompt):

  arcpy.ia.DetectObjectsUsingDeepLearning(
    imagenEntradaModelo, 
    rutaDeSalida, 
    textSAM_dlpk, 
    [
      ["text_prompt", prompt], 
      ["padding", "256"], 
      ["batch_size", "4"], 
      ["box_threshold", "0,3"], 
      ["text_threshold", "0,2"], 
      ["box_nms_thresh", "0,7"]
    ], 
    "NO_NMS", 
    "Confidence", 
    "Class", 
    0, 
    "PROCESS_AS_MOSAICKED_IMAGE"
  )

dFSalida = pd.DataFrame(columns = ['FID Image', 'VehiclesCount', 'Date'])

# Configuración del Bucle que recorre todos los elementos
  
for FID in range(len(camarasTraficoDF)):

  print(f'Iteración nº: {FID}')

  # LLamada al Servicio
  
  response = requests.get(camarasTraficoDF.iloc[FID,6])

  # Abro la imagen y la guardo

  responseImage = Image.open(BytesIO(response.content))

  responseImage.save(os.path.join(rutaCarpetaImagenes,f'imagenDGT{FID}.jpg'))

  urlIm = os.path.join(rutaCarpetaImagenes,f'imagenDGT{FID}.jpg')

  # Configuro el nombre de la layer que nos devuelve la herramienta de geoproceso

  layerName = f'resultadoImagen{FID}'
  
  layerOutputUrl = os.path.join(rutaGDB, layerName)

  # Ejecuto la herramienta

  DetectDGT(urlIm, layerOutputUrl,'car, vehicle')

  numeroVehiculos = arcpy.GetCount_management(layerName).getOutput(0)

  dFSalida.loc[len(dFSalida.index)] = [f'imagenDGT{FID}', float(numeroVehiculos), datetime.now()]

# Exportl el DF a excel
  
nombreXLSXSalida = 'dFSalida.xlsx'

dFSalida.to_excel(os.path.join(directorioTrabajo,nombreXLSXSalida))

