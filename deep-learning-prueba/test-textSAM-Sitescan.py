# Importamos las librerías necesarias

from arcgis.gis import GIS
import os
import arcpy
from arcpy.ia import *
from datetime import datetime

horaInicio = datetime.now()

# Conectamos a ArcGIS Online

gis = GIS("home")

# ¡¡IMPORTANTE INSERTA LA RUTA DEL DIRECTORIO DE TRABAJO!!ç
# Por favor crea una nueva carpeta donde se guarde la ejecución

directorioTrabajo = 'C:\\Users\\alvaro.gutierrez\\DatosLocal\\PruebaSitescan'

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

# INserta Ruta del TextSAM.dlpk

textSAM_dlpk = "C:/Users/alvaro.gutierrez/DatosLocal/Imagenes-deep-learning/DeepLearningPackage/TextSAM.dlpk"


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

# Abro la imagen

nombreImagen = 'DJI_0357.jpg'

urlIm = os.path.join(directorioTrabajo,nombreImagen)

# Configuro el nombre de la layer que nos devuelve la herramienta de geoproceso

layerName = 'resultadoImagen'

layerOutputUrl = os.path.join(rutaGDB, layerName)

# Ejecuto la herramienta

DetectDGT(urlIm, layerOutputUrl,'tree')

numeroArboles = arcpy.GetCount_management(layerName).getOutput(0)

print( f'Número de árboles: {numeroArboles}')

horaFin = datetime.now()

tiempoTotal = horaFin-horaInicio

print(tiempoTotal)
