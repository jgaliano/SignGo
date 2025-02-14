from django.shortcuts import render, redirect
from django.http import HttpResponse
import random
import os
from django.conf import settings
from . models import documentos, firmante
import requests
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

def validatePermissions(user):
    return user.groups.filter(name='eSignAuth').exists()

# Create your views here.
def helloworld(request):
    return render(request, 'eSignAnyWhere/helloworld.html')

@login_required
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
def uplaodFile(request):
    if request.method == 'GET':
        return render(request, 'eSignAnyWhere/uploadFile.html')
    else: 
        nombre_archivos = []
        pdf_files = request.FILES.getlist('pdf_files')
        
        nombreCarpeta = random.randint(100000000000000, 999999999999999)         
        nuevaCarpeta = os.path.join(settings.MEDIA_ROOT, 'eSignAnyWhere/FilesToSign/', str(nombreCarpeta))
        os.mkdir(str(nuevaCarpeta))
        nuevaCarpetaReporte = os.path.join(settings.MEDIA_ROOT, 'eSignAnyWhere/FilesSigned/', str(nombreCarpeta))
        os.mkdir(str(nuevaCarpetaReporte))
        rutaCarpeta = 'eSignAnyWhere/FilesToSign/' + str(nombreCarpeta) + '/'
        destino_carpeta = os.path.join(settings.MEDIA_ROOT, rutaCarpeta)
        
        for pdf_file in pdf_files:
            nombre_inicial = pdf_file.name
            nombre_archivos.append(nombre_inicial)
            destino_archivo_nuevo = os.path.join(destino_carpeta, nombre_inicial)
            
            with open(destino_archivo_nuevo, 'wb') as archivo_destino:
                for parte in pdf_file.chunks():
                    archivo_destino.write(parte)
                    
        newURL = "/eSignAnyWhere/viewDocument/" + str(nombreCarpeta)
        
        postDocumentos = documentos(
            nombreArchivos = nombre_archivos,
            nombreCarpeta = nombreCarpeta,
            estatus = "pending"
        )
        postDocumentos.save()
        
        return redirect(newURL)

@login_required
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
def viewDocument(request, requestID):
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
            #Enviar Documento para firmar
            sendDocument = uploadDocument(documento, requestID)
            
        postData = documentos.objects.get(nombreCarpeta=requestID)
        postData.request = sendDocument
        postData.save()
        newURL = '/eSignAnyWhere/formData/' + str(requestID)
        return redirect(newURL)
    
    return render(request, 'eSignAnyWhere/previewDocument.html', contexto)
    
def uploadDocument(documento, requestID):
    
    url = "https://demo.esignanywhere.net/Api/v6/file/upload"

    payload = {}
    
    base_path = './media/eSignAnyWhere/FilesToSign/' + str(requestID) + '/'
    file_path = os.path.join(base_path, documento)
    
    files = [
        ('file', (documento, open(file_path,'rb'),'application/pdf'))
    ]
    
    headers = {
        'ApiToken': 'rlub4d0znsglptcq5v0sfkt3r1d7muxeum2lr9b4b1pynqb3vw5zhciku0nuat6i'
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    idSign = json.loads(response.text)
    fileId = idSign.get('FileId')
    return fileId

def sendDataUser(idFile, idRequest, tipoFirma):

    url = "https://demo.esignanywhere.net/Api/v6/envelope/send"
    
    getDataCliente = firmante.objects.get(request=idRequest)

    payload = json.dumps({
        "Documents": [
            {
            "FileId": idFile,
            "DocumentNumber": 1
            }
        ],
        "Name": getDataCliente.sobre,
        "Activities": [
            {
            "Action": {
                "Sign": {
                "RecipientConfiguration": {
                    "ContactInformation": {
                    "Email": getDataCliente.correo,
                    "GivenName": getDataCliente.nombres,
                    "Surname": getDataCliente.apellidos,
                    "LanguageCode": "ES"
                    }
                },
                "Elements": {
                    "Signatures": [
                    {
                        "ElementId": "sample sig click2sign",
                        "Required": True,
                        "DocumentNumber": 1,
                        "DisplayName": "Sign here",
                        "AllowedSignatureTypes": {
                            tipoFirma: {}
                        },
                        "FieldDefinition": {
                        "Position": {
                            "PageNumber": 1,
                            "X": 100,
                            "Y": 200
                        },
                        "Size": {
                            "Width": 100,
                            "Height": 70
                        }
                        }
                    }
                    ]
                },
                "SigningGroup": "firstSigner"
                }
            }
            },
            {
            "Action": {
                "SendCopy": {
                "RecipientConfiguration": {
                    "ContactInformation": {
                    "Email": "jgaliano@ccg.gt",
                    "GivenName": "Galiano",
                    "Surname": "Test",
                    "LanguageCode": "ES"
                    }
                }
                }
            }
            }
        ]
    })
    headers = {
        'ApiToken': 'rlub4d0znsglptcq5v0sfkt3r1d7muxeum2lr9b4b1pynqb3vw5zhciku0nuat6i',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    dataEnv = json.loads(response.text)
    return dataEnv.get('EnvelopeId')

@login_required  
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
def formData(request, requestID):
    if request.method == 'POST':
        nombreSobre = request.POST['nombreSobre']
        nombreUsuario = request.POST['nombreDestinatario']
        apellidoUsuario = request.POST['apellidoDestinatario']
        emailUsuario = request.POST['emailDestinatario']
        tipoFirma = request.POST['tipoCertificado']
        
        if tipoFirma == "1":
            tipoSign = "DrawToSign"
        else: 
            tipoSign = "LocalCertificate"
        
        saveDataFirmante = firmante (
            nombres = nombreUsuario,
            apellidos = apellidoUsuario,
            correo = emailUsuario,
            sobre = nombreSobre,
            request = requestID,
            tipo = tipoSign
        )
        saveDataFirmante.save()
        
        getData = documentos.objects.get(nombreCarpeta=requestID)
        idFileRequest = getData.request

        sendInfoDestinatario = sendDataUser(idFileRequest, requestID, tipoSign)
        
        postEnvelopeRequest = firmante.objects.get(request=requestID)  
        postEnvelopeRequest.envelope = sendInfoDestinatario 
        postEnvelopeRequest.save()
        
        return redirect('/eSignAnyWhere/confirmacionEnvio/' + str(requestID))
    
    print(requestID)
    return render(request, 'eSignAnyWhere/formUser.html')

@login_required
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
def confirmacionEnvio(request, requestID):
    return render(request, 'eSignAnyWhere/confirmacionEnvio.html')

@login_required
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
def solicitudes(request):
    getDataFirmante = firmante.objects.all()
    contexto = {
        'dataFirmantes': getDataFirmante
    }
    return render(request, 'eSignAnyWhere/solicitudes.html', contexto)

@login_required
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
def solicitud(request, requestID):
    
    getDataFirmante = firmante.objects.get(request=requestID)
    getDataDocumento = documentos.objects.get(nombreCarpeta=requestID)
    
    getDocumentos = documentos.objects.get(nombreCarpeta=requestID)
    getNameDocs = getDocumentos.nombreArchivos
    viewDocuments = []
    filesSigned = []
    
    for documento in getNameDocs:
        viewDocuments.append([documento, '310KB'])
    
    if getDataDocumento.estatus == "pending":
        getStatusFile = getStatusSign(getDataFirmante.envelope)
        getStatusFile
        if getStatusFile == "Pending":
            resultado = "Pendiente de Firma"
            filesSigned = []
        else: 
            resultado = "Firmado"
            idFiles = getIDFiles(getDataFirmante.envelope)
            fileDownload = downloadFile(idFiles, getDataFirmante.envelope)
            print(fileDownload)
            getDataDocumento.estatus = resultado
            getDataDocumento.save()
            filesSigned = viewDocuments
    else: 
        resultado = "Firmado"
        filesSigned = viewDocuments
    
    
        
    contexto = {
        'dataFirmante': getDataFirmante,
        'statusFiles': resultado,
        'documentos': viewDocuments,
        'carpeta': requestID,
        'filesSigned': filesSigned
    }
    
    return render(request, 'eSignAnyWhere/solicitud.html', contexto)

def getStatusSign(envelope):

    url = "https://demo.esignanywhere.net/Api/v6/envelope/" + str(envelope)

    payload = {}
    headers = {
        'ApiToken': 'rlub4d0znsglptcq5v0sfkt3r1d7muxeum2lr9b4b1pynqb3vw5zhciku0nuat6i'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    requestStatus = json.loads(response.text)

    return requestStatus.get('Activities')[0].get('Status')

def getIDFiles(envelope):

    url = "https://demo.esignanywhere.net/Api/v6/envelope/" + str(envelope) + "/files"

    payload = {}
    headers = {
        'ApiToken': 'rlub4d0znsglptcq5v0sfkt3r1d7muxeum2lr9b4b1pynqb3vw5zhciku0nuat6i'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    idFile = json.loads(response.text)
    
    return idFile.get('Documents')[0].get('FileId')

def downloadFile(fileId, envelopeID):

    url = "https://demo.esignanywhere.net/Api/v6/file/" + str(fileId)

    payload = {}
    
    headers = {
        'ApiToken': 'rlub4d0znsglptcq5v0sfkt3r1d7muxeum2lr9b4b1pynqb3vw5zhciku0nuat6i'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    
    getRequest = firmante.objects.get(envelope=envelopeID)
    getNameDocs = documentos.objects.get(nombreCarpeta=getRequest.request)
    
    for documento in getNameDocs.nombreArchivos:
        nameDoc = documento

    # fileDirectorio = os.path.join('media', 'eSignAnyWhere', 'FilesSigned', getRequest.request)
    # os.makedirs(fileDirectorio)
    file_path = os.path.join('media', 'eSignAnyWhere', 'FilesSigned', getRequest.request, f'{nameDoc}')
    
    with open(file_path, 'wb') as f:
        f.write(response.content)
        
    return "200 Ok"