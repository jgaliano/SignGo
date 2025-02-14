from django.shortcuts import render
import os
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.db import connection, OperationalError
from django.conf import settings

# Create your views here.
@csrf_exempt
def url_out(request, carpeta, name):
    
    ruta_destino = "./media/signbox/FilesFirmados/" + carpeta

    if not os.path.isdir(ruta_destino):
        nuevaCarpeta = os.path.join(settings.MEDIA_ROOT, 'signbox/FilesFirmados/', carpeta)
        os.mkdir(str(nuevaCarpeta))
    
    if request.method == 'POST':
        ruta = os.path.abspath(os.getcwd())
        data = request.body
        os.chdir(ruta)
        
        ruta_completa = os.path.join(ruta_destino, name)
        with open(ruta_completa, 'wb') as f:
            f.write(data)
          
    return HttpResponse('OK', status=200)
    
    

@csrf_exempt
def urlback(request, name):
    if request.method == 'POST':
        today = datetime.now() 
        data = request.body
        print(today)
        print(data)
    
    return HttpResponse('OK', status=200)

@csrf_exempt
def url_out_planilla(request, carpeta, id, name):
    ruta_destino_base = os.path.join(settings.MEDIA_ROOT, 'pagoPlanilla', 'boletasSign', carpeta)
    
    if not os.path.exists(ruta_destino_base):
        os.makedirs(ruta_destino_base, exist_ok=True)

    ruta_directorio_id = os.path.join(ruta_destino_base, str(id))
    if not os.path.exists(ruta_directorio_id):
        os.makedirs(ruta_directorio_id, exist_ok=True)

    if request.method == 'POST':
        ruta_completa = os.path.join(ruta_directorio_id, name)
        
        try:
            with open(ruta_completa, 'wb') as archivo:
                archivo.write(request.body)
            return HttpResponse('OK', status=200)
        except Exception as e:
            return HttpResponse(f'Error al guardar el archivo: {str(e)}', status=500)
    return HttpResponse('Método no permitido', status=405)