from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from datetime import datetime
import requests
from django.db import connection, OperationalError
import os
from django.contrib import messages
from django.shortcuts import render, redirect
import json
import secrets
import random
from . models import documentos, requestValidation
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test

def validatePermissions(user):
    return user.groups.filter(name='VolAuth').exists()

# Create your views here.
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
def helloworld(request):
    return render(request, 'vol/helloworld.html')

@login_required
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
def home(request):
    if request.method == 'GET':
        return render(request, 'vol/vol_cargadPDF.html')
    else: 
        nombre_archivos = []
        pdf_files = request.FILES.getlist('pdf_files')
        
        nombreCarpeta = random.randint(100000000000000, 999999999999999)         
        nuevaCarpeta = os.path.join(settings.MEDIA_ROOT, 'vol/FilesValidar/', str(nombreCarpeta))
        os.mkdir(str(nuevaCarpeta))
        nuevaCarpetaReporte = os.path.join(settings.MEDIA_ROOT, 'vol/Reportes/', str(nombreCarpeta))
        os.mkdir(str(nuevaCarpetaReporte))
        rutaCarpeta = 'vol/FilesValidar/' + str(nombreCarpeta) + '/'
        destino_carpeta = os.path.join(settings.MEDIA_ROOT, rutaCarpeta)
        
        for pdf_file in pdf_files:
            nombre_inicial = pdf_file.name
            nombre_archivos.append(nombre_inicial)
            destino_archivo_nuevo = os.path.join(destino_carpeta, nombre_inicial)
            
            with open(destino_archivo_nuevo, 'wb') as archivo_destino:
                for parte in pdf_file.chunks():
                    archivo_destino.write(parte)
                    
        newURL = "/vol/verifyDocs/" + str(nombreCarpeta)
        
        postDocumentos = documentos(
            nombreArchivos = nombre_archivos,
            nombreCarpeta = nombreCarpeta
        )
        postDocumentos.save()
        
        return redirect(newURL)

@login_required
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
def verificarDocumentos(request, requestID):
    print("función verificarDocumentos")
    getDocumentos = documentos.objects.get(nombreCarpeta=requestID)
    getNameDocs = getDocumentos.nombreArchivos
    viewDocuments = []
    documentosValidados = []
    for documento in getNameDocs:
        viewDocuments.append([documento, '310KB'])
        
    contexto = {
        'documentos': viewDocuments,
        'carpeta': requestID
    }
    
    if request.method == "POST":
        for documento in getNameDocs:
            #Enviar Documento para validar
            sendDocument = requestVol(documento, requestID)
            getVerification = verificationDoc(sendDocument)
            validate1 = getVerification['errors'][0]['what']
            documentosValidados.append(validate1)
            postValidation = requestValidation(
                requestVol=requestID,
                result=documentosValidados,
                identificador=sendDocument,
                documento=documento
            )
            postValidation.save()
            
            getReport = generateReport(sendDocument, documento, requestID)
            print(getReport)
            
            newURL = '/vol/validate/' + str(requestID)
        return redirect(newURL)
    
    return render(request, 'vol/vol_verificarDocs.html', contexto)


def requestVol(requestDoc, carpeta):
    print("función requestVol")
    url = "http://10.10.10.9:8085/api/documents/"

    fileToSend = requestDoc
    routeFile = "./media/vol/FilesValidar/" + str(carpeta) + "/" + fileToSend

    payload = {}
    files=[
        ('document',(fileToSend,open(routeFile,'rb'),'application/pdf'))
    ]
    
    headers = {
        'Authorization': 'Basic cHJlcHJvZEBjY2c6UGJjMTIzKio='
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    data = json.loads(response.text)

    data_refactor = data['location']
    data_send = data_refactor.split('/documents/')
    return str(data_send[1])

def verificationDoc(requestId):
    print("función verificationDoc")
    url = "http://10.10.10.9:8085/api/documents/" + str(requestId) + "/verify/report?type=json&template=report"

    headers = {
        'Authorization': 'Basic cHJlcHJvZEBjY2c6UGJjMTIzKio='
    }

    try:
        response = requests.get(url, headers=headers)  # Timeout de 15 segundos
        print(f"Estado de la respuesta: {response.status_code}")
    except requests.Timeout:
        print("La solicitud excedió el tiempo de espera")
    except requests.RequestException as e:
        print(f"Error en la solicitud: {e}")

    return(json.loads(response.text))

@login_required
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
def documentosValidados(request, requestID):
    print("función documentosValidados")
    viewDocuments = []
    getValidation = requestValidation.objects.filter(requestVol=requestID)
    for validate in getValidation:
        print(validate.documento)   
        print(validate.result[0])
        print(validate.identificador)
        viewDocuments.append([validate.documento, validate.result[0]])
    
    contexto = {
        'documentos': viewDocuments,
        'carpeta': requestID,
        'addressReporte': 'Reportes',
        'addressOriginal': 'FilesValidar'
    }
    
    return render(request, 'vol/vol_getResponse.html', contexto)


def generateReport(idVol, fileToSend, carpeta):
    print("función generateReport")
    routeFile = "./media/vol/Reportes/" + str(carpeta)

    url = "http://10.10.10.9:8085/reports?documentid=" + idVol

    headers = {
    'Authorization': 'Basic cHJlcHJvZEBjY2c6UGJjMTIzKio='
    }

    response = requests.request("GET", url, headers=headers)
    newName = os.path.join(routeFile, fileToSend)
    
    with open(newName, 'wb') as file:
        file.write(response.content)
    
    return "Listo"






    


    
