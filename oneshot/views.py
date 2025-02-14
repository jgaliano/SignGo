from django.shortcuts import render
import requests
import json
import os
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db import connection, OperationalError
from django.conf import settings
import random
import string
import hashlib
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.http import HttpResponse
from datetime import datetime
from .models import cliente, requestSign, documentos, oneshotAPI, billingOneshotProd, billingOneshotSandbox
import secrets
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import user_passes_test

def validatePermissions(user):
    return user.groups.filter(name='OneshotAuth').exists()

def helloworld(request):
    return render(request, 'oneshot/one_shot_vistaCorreo.html')

def getIPOneshotAPI():
    dataOneshot = oneshotAPI.objects.get(id=1)
    protocolOneshot = "http" if dataOneshot.protocol == "0" else "https"
    ipOneshot = dataOneshot.ip
    endpointOneshot = protocolOneshot + "://" + ipOneshot
    return endpointOneshot

def one_shot_createRequest(request, data_request, imagenes):
    
        dataBillingProd = billingOneshotProd.objects.get(id=1)
        dataBillingSandbox = billingOneshotSandbox.objects.get(id=1)
        
        if dataBillingSandbox.status == "1":
            userBilling = dataBillingSandbox.user
            passBilling = dataBillingSandbox.password
        else:
            userBilling = dataBillingProd.user
            passBilling = dataBillingProd.password

        imagen_request = imagenes
        
        ip = getIPOneshotAPI()

        url = ip + "/api/v1/request"
    
        new_phone_number = '+502' + data_request[5]

        nombre_completo = data_request[0] + " " + data_request[10] 
                
        payload={'given_name': nombre_completo,
        'surname_1': data_request[1],
        'surname_2': data_request[2],
        'id_document_type': 'IDC',
        'id_document_country': 'GT',
        'serial_number': data_request[3],
        'email': data_request[4],
        'mobile_phone_number': new_phone_number,
        'registration_authority': '98',
        'profile': 'CCPNIndividual',
        'username': data_request[6],
        'password': data_request[7],
        'pin': data_request[8],
        'env': 'sandbox',
        'billing_username': 'ccg@ccg',
        'billing_password': 'dDJHOVQ3MU8=',
        'residence_city': 'Guatemala',
        'residence_address': data_request[9]}
        payload_json = json.dumps(payload)

        files = {
            'document_front': ('img_front.jpg', imagen_request[0], 'image/jpg'),
            'document_rear': ('img_rear.jpg', imagen_request[1], 'image/jpg'),
            'document_owner': ('img_owner.jpg', imagen_request[2], 'image/jpg')
        }

        response = requests.post(url, data=payload, files=files)

        print("Se crea request")
        print(url)
        print(response.text)

        return response.text

def one_shot_sendDocument(request):
    
    ip = getIPOneshotAPI()
    
    info_sessin = request.session.get('context_data', {})
    id_transaction = info_sessin.get('idRequest')
    url_before = ip + "/api/v1/document/"
    url = url_before + str(id_transaction)

    payload={}

    base_path = './media/oneshot/FilesNoFirmados/'
    
    name_archivos = []
    name_archivos = request.session['archivos_carga']
    request_name = name_archivos['archivos_in']

    file_names = request_name

    files = []

    for file_name in file_names:
        file_path = os.path.join(base_path, file_name)
        files.append(('file', (file_name, open(file_path,'rb'), 'application/pdf')),)
    
    try:
            response = requests.request("POST", url, data=payload, files=files)
            data = response.text
            print("Documento Enviado al API")
            print(url)
            print(payload)
            print(response.text)
            return data
        
    except Exception as e:
            return print(f'No se pudo enviar el documento: {e}') 

def sendOTP(request):
    
    ip = getIPOneshotAPI()
    
    info_sessin = request.session.get('context_data', {})
    id_transaction = info_sessin.get('idRequest')
    url_before = ip + "/api/v1/otp/"
    url = url_before + str(id_transaction)
    
    response = requests.post(url)
    data = response.json()
    return data

def requestConVideoID(datosCliente):
    ip = getIPOneshotAPI()
    url = ip + "/api/v1/videoid"
    
    # Información Cliente
    new_phone_number = '+502' + datosCliente[5]
    nombre_completo = datosCliente[0] + datosCliente[9] 

    payload = json.dumps({
        "mobile_phone_number": new_phone_number,
        "email": datosCliente[4],
        "registration_authority": "98",
        "profile": "CCPNIndividual",
        "residence_city": "Guatemala",
        "residence_address": "Guatemala",
        'given_name': nombre_completo,
        'surname_1': datosCliente[1],
        'surname_2': datosCliente[2],
        "videoid_mode": True,
        "billing_username": "ccg@ccg",
        "billing_password": "dDJHOVQ3MU8=",
        "env": "sandbox"
        })

    response = requests.post(url, data=payload)
    
    return response.text

@login_required
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
def formulario(request):
    if request.method == 'GET':        
        return render(request, 'oneshot/one_shot_home.html')
    else:
        data_request = []
        data_request.append(request.POST['inputName']) # given_name
        data_request.append(request.POST['inputApellido1']) # surname_1
        data_request.append(request.POST['inputApellido2']) # surname_2
        data_request.append(request.POST['inputDPI']) # serial_number
        data_request.append(request.POST['inputEmail']) # email
        data_request.append(request.POST['inputCelular']) # mobile_phone_number
        data_request.append(request.POST['usuario']) # username
        data_request.append(request.POST['contraseña']) # password
        data_request.append(request.POST['pin']) # pin
        data_request.append(request.POST['inputAddress']) # address
        data_request.append(request.POST['inputSecondName'])
        
        imagenes = []
        imagenes.append(request.FILES['formFile1'])
        imagenes.append(request.FILES['formFile2'])
        imagenes.append(request.FILES['formFile3'])
        
        # Proceso de verificación si se requiere VideoID
        requestVideoID = request.POST.get('videoId')
        if requestVideoID:
            
            dataRequest = requestConVideoID(data_request) # json con la respuesta del api con id de video y request
            get_json = json.loads(dataRequest)
            
            idVideo = get_json['details']['videoid_pk']
            idRequest = get_json['details']['request_pk']

            idTransac_send = str(idRequest)
            correo_send = request.POST['inputEmail']
            name1_send = request.POST['inputName']
            name2_send = request.POST['inputSecondName']
            apellido1_send = request.POST['inputApellido1']
            apellido2_send = request.POST['inputApellido2']
            dpi_send = request.POST['inputDPI']
            email_send = request.POST['inputEmail']
            celular_send = request.POST['inputCelular']
            address_send = request.POST['inputAddress']
            
            insert_cliente = cliente(
                primer_nombre = name1_send,
                segundo_nombre = name2_send,
                primer_apellido = apellido1_send,
                segundo_apellido = apellido2_send,
                email = email_send,
                direccion = address_send,
                dpi = dpi_send,
                celular = celular_send,
                status = "No Firmado",
                tipo = "Con Video ID"
            )
            
            nombre_completo = name1_send + " " + name2_send + " " + apellido1_send + " " + apellido2_send
            
            insert_cliente.save()
            
            secret_cliente = secrets.token_urlsafe(50)
            secret_operador = secrets.token_urlsafe(50)
            
            insert_request = requestSign(
                id_request = idTransac_send,
                id_cliente = insert_cliente,
                transaction_cliente = secret_cliente,
                transaction_operador = secret_operador,
                correo_operador = request.user.email,
                username_operador = request.user.username,
                id_video = idVideo,
                aprovado = "No"
            )
            
            insert_request.save()
            
            return render(request, 'oneshot/one_shot_videoId.html',  {"correo":email_send, 'nombre':nombre_completo})
        else:             
            enviar = one_shot_createRequest(request, data_request, imagenes)
            
            get_json = json.loads(enviar)
            responde_details = get_json['details']
        
            idTransac_send = str(responde_details)
            correo_send = request.POST['inputEmail']
            name1_send = request.POST['inputName']
            name2_send = request.POST['inputSecondName']
            apellido1_send = request.POST['inputApellido1']
            apellido2_send = request.POST['inputApellido2']
            dpi_send = request.POST['inputDPI']
            email_send = request.POST['inputEmail']
            celular_send = request.POST['inputCelular']
            address_send = request.POST['inputAddress']
            
            context_data = {
                'correo': correo_send, 
                'idRequest': idTransac_send,
                'name': name1_send,
                'name2': name2_send,
                'apellido1': apellido1_send,
                'apellido2': apellido2_send,
                'dpi': dpi_send,
                'email': email_send,
                'celular': celular_send,
                'address': address_send
            }
            request.session['context_data'] = context_data
            
            insert_cliente = cliente(
                primer_nombre = name1_send,
                segundo_nombre = name2_send,
                primer_apellido = apellido1_send,
                segundo_apellido = apellido2_send,
                email = email_send,
                direccion = address_send,
                dpi = dpi_send,
                celular = celular_send,
                status = "No Firmado",
                tipo = "Sin Video ID"
            )
            
            insert_cliente.save()
            
            secret_cliente = secrets.token_urlsafe(50)
            secret_operador = secrets.token_urlsafe(50)
            
            insert_request = requestSign(
                id_request = idTransac_send,
                id_cliente = insert_cliente,
                transaction_cliente = secret_cliente,
                transaction_operador = secret_operador,
                correo_operador = request.user.email,
                username_operador = request.user.username,
                id_video = "None",
                aprovado = "No"
            )
            
            insert_request.save()
            
            return redirect('one_shot_docs')


@login_required  
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')            
def one_shot_cargarPDFs(request):
    if request.method == 'GET':
        return render(request, 'oneshot/one_shot_cargarPDF.html')
    else:
        nombre_archivos = []
        pdf_files = request.FILES.getlist('pdf_files')
        destino_carpeta = os.path.join(settings.MEDIA_ROOT, 'oneshot/FilesNoFirmados/')
        x = 0
        
        info_sessin = request.session.get('context_data', {})
        id_transaction = info_sessin.get('idRequest')
        
        for pdf_file in pdf_files:
            nombre_inicial = pdf_file.name
            nombre_recortado = nombre_inicial.split(".pdf")
            nombre_nuevo = nombre_recortado[0] + "_" + id_transaction + ".pdf"
            nombre_archivos.append(nombre_nuevo)
            
            destino_archivo_nuevo = os.path.join(destino_carpeta, nombre_nuevo)
            
            with open(destino_archivo_nuevo, 'wb') as archivo_destino:
                for parte in pdf_file.chunks():
                    x+= 1
                    archivo_destino.write(parte)
        
        print("Archivos Cargador")
        
        context_archivos = {
                'archivos_in': nombre_archivos
            }
        request.session['archivos_carga'] = context_archivos
        
        send_document = one_shot_sendDocument(request)
        
        request_docs = []
        if x > 1:
            data_documento = json.loads(send_document)
            filtrar_docs = [detalle["uid"] for detalle in data_documento["details"]]    
            for docs in filtrar_docs:
                request_docs.append(docs)
        elif x == 1:
            data_documento = json.loads(send_document)
            valor_details = data_documento  ["details"]
            request_docs.append(valor_details)
            
        context_archivos = {
            'name_docs': request_docs
        }
        
        request.session['context_archivos'] = context_archivos
        
        archivos_nombres = json.dumps(nombre_archivos)
        context_data = request.session.get('context_data', {})
        correo_ingresado = context_data.get('correo')
        request_oneshot = context_data.get('idRequest')
        name_in = context_data.get('name')
        name2_in = context_data.get('name2')
        apellido1_in = context_data.get('apellido1')
        apellido2_in = context_data.get('apellido2')
        email_in = context_data.get('email')
        
        insert_document = documentos(
            id_request = request_oneshot,
            status = "NoFirmado",
            transaction = request_docs,
            name_archivos = nombre_archivos
        )
        
        insert_document.save()

        valor_secret_document = requestSign.objects.filter(id_request=request_oneshot).values('transaction_cliente')
        
        if valor_secret_document.exists():
            valor_secret = valor_secret_document.first()['transaction_cliente']
        else:
            valor_secret = None
        
        remitente = 'noreply@camaradecomercio.org.gt'  # Dirección de correo del remitente
        destinatario = email_in
        asunto = "Documentos para firmar"
        # mensaje = "https://demofirma.camaradecomercio.com.gt/profile/" + str(contrasena)
        mensaje = "http://localhost:8080/oneshot/profile/" + str(valor_secret)
        
        context = {
            'data': mensaje,
            'nombre': name_in,
            'apellido': apellido1_in
        }
        
        nombre_completo = name_in + " " + name2_in + " " + apellido1_in + " " + apellido2_in
        
        template_html = render_to_string('oneshot/one_shot_PlantillaCorreo.html', context)
        
        try:
            send_mail(
                asunto,  # Asunto del correo
                '',  # Contenido del correo
                remitente,  # Correo del remitente
                [destinatario],  # Lista de destinatarios
                fail_silently=False,  # Si se establece en True, los errores no se levantarán sino que se registrarán en la consola
                html_message=template_html
            )
            print("Correo Enviado")
            return render(request, 'oneshot/one_shot_viewDocument.html',  {"correo":correo_ingresado, 'nombre':nombre_completo})
        except Exception as e:
            print(f"Error al enviar el correo: {e}")
            
        return render(request, 'oneshot/one_shot_viewDocument.html',  {"correo":correo_ingresado, 'nombre':nombre_completo})

@login_required  
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
def profile(request):
    username = "1"
    username2 = "dGyRjWmBoNpSqUtXwZkElYiCvAhTgFmJeHlLoPrM"
    return render(request, 'profile.html', {'username': username})


def user_profile(request, username):
    if request.method == 'GET':
        ruta_exacta = request.path
        ruta_formateada = str(ruta_exacta).split('oneshot/profile/')
        
        ruta_direct = {
            'url': ruta_exacta
        }
        request.session['url_exacta'] = ruta_direct

        anw = ruta_formateada[1]
        new_url = anw[:-1]
        
        valor_a_verificar = new_url

        id_request = requestSign.objects.filter(transaction_cliente=valor_a_verificar).values('id_request', 'id_cliente', 'correo_operador', 'transaction_operador')
        
        if id_request.exists():
            for valores_request in id_request:
                request_sign = valores_request['id_request']
                id_cliente = valores_request['id_cliente']
                correo_operador = valores_request['correo_operador']
                transaction_operador = valores_request['transaction_operador']

            request_name = cliente.objects.filter(id=id_cliente).values(
                'primer_nombre', 
                'segundo_nombre',
                'primer_apellido',
                'segundo_apellido'
            )
            
            for nombre in request_name:
                nombre_completo = str(nombre['primer_nombre']) + " " + str(nombre['segundo_nombre']) + " " + str(nombre['primer_apellido']) + " " + str(nombre['segundo_apellido'])
            
            valor_documentos = documentos.objects.filter(id_request=request_sign).values('name_archivos')
            idRequestDocs = documentos.objects.filter(id_request=request_sign).values('transaction')
            
            if valor_documentos.exists():
                cadena_nombres = valor_documentos.first()['name_archivos']
                idDocs = idRequestDocs.first()['transaction']
            
            # print("Id de documentos")
            # print(idDocs)
            # print("Request Oneshot")
            # print(request_sign)
            
            context_archivos = {
                'name_docs': cadena_nombres
            }
            
            request.session['nombre_archivos'] = context_archivos
            
            nombre_archivos = []
            x = 0

            for nombre in cadena_nombres:
                x+= 1
                nombre_archivos.append([x, nombre, '310KB'])
            
            
            data_otp = request.session.get('context_OTP', {})
            status_otp = data_otp.get('status')
                
            if status_otp == "0":
                estado_OTP = "0"
            else: 
                estado_OTP = "1"
             
            contexto = {
                'username': nombre_completo,
                'resultados': nombre_archivos,
                'status': estado_OTP,
                'request': request_sign,
            }
            
            dataNew_template = {
                'username': nombre_completo,
                'resultados': nombre_archivos,
                'request': request_sign,
                'idRequestFiles': idDocs,
                # 'dpiUsuario': dpi_usuario,
                'idHash': transaction_operador,
                'email_operador': correo_operador
                }
            request.session['data_template'] = dataNew_template
            
            return render(request, 'oneshot/one_shot_vistaCorreo.html', contexto)
        else:
            return render(request, 'oneshot/one_shot_ERROR.html')
    else:
        ip = getIPOneshotAPI()
        url_before = ip + "/api/v1/otp/"
        
        info_sessin = request.session.get('context_data', {})
        id_transaction = info_sessin.get('idRequest')
        url = url_before + id_transaction

        payload = json.dumps({
            "delivery_method": "whatsapp"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)
        
def one_shot_sign(request):
    ip = getIPOneshotAPI()
    if request.method == 'GET':
        
        # variable = "['450689f7-a0bb-4bc5-aad3-0f790160a9e8']"
        # idRequestSign = documentos.objects.get(transaction=variable)
        
        info_sessin = request.session.get('data_template', {})
        id_transaction = info_sessin.get('request')
        print(id_transaction)
        
        url_before = ip + "/api/v1/sign/"
        url = url_before + str(id_transaction)
        print(url)
        
        return HttpResponse("Esta página solo acepta peticiones POST")
    else:
        
        info_sessin = request.session.get('data_template', {})
        id_transaction = info_sessin.get('request')
        
        url_before = ip + "/api/v1/sign/"
        url = url_before + str(id_transaction)
        
        secretOTP = request.POST['codigo']
        
        info_sessin = request.session.get('data_template', {})
        id_files = info_sessin.get('idRequestFiles')
        cadena = id_files.strip('{}')
        valores = cadena.split(',')
        valores = [valor.strip().strip('"}') for valor in valores]
        request_docs = valores        
        
        payload = {
            "secret": secretOTP,
            "disable_ltv": True,
            "use_signature_text": True,
            "options": {}
        }
        
        # "image": "bbaac1c9-a92f-4606-a326-ec1e7548e93f",
        
        for i, doc in enumerate(request_docs):
            newDoc = doc.strip("[]'\"")
            print(url + newDoc)
            payload["options"][newDoc] = {
                "position": "300, 100, 500, 150",
                "page": "0"
            }
        
        response = requests.post(url, json=payload)
        data = response.json()
        print(data)
        
        hola = getDocuments(request)
        print(hola)
        
        status_details = data['status']
        
        if status_details == "200 OK":
            context_OTP = request.session.get('context_OTP', {})
            context_OTP['status'] = '1' 
            request.session['context_OTP'] = context_OTP
            send_correo = sendCorreOperador(request)
            print(send_correo)
            
            estado = "Firmado"
            
            updateStatusDoc = documentos.objects.get(id_request=id_transaction)
            updateStatusDoc.status = estado
            updateStatusDoc.save()
            
            # Update Status Firmado Cliente
            getDataRequest = requestSign.objects.get(id_request=id_transaction)
            getDataCliente = cliente.objects.get(id=getDataRequest.id_cliente_id)
            getDataCliente.status = estado
            getDataCliente.save()
            
            return redirect('one_shot_Firmados')
        elif "OTP":
            info_sessin = request.session.get('url_exacta', {})
            current_path = info_sessin.get('url')
            context_OTP = {
                'status': '0'
            }
            
            request.session['context_OTP'] = context_OTP
            return redirect(current_path)

        return redirect('one_shot_Firmados')
       
def getDocuments(request):

    name_archivos = []
    name_archivos = request.session['nombre_archivos']
    request_name = name_archivos['name_docs']
    x = 0
    
    for request_doc in request_name:
 
        info_sessin = request.session.get('data_template', {})
        id_transaction = info_sessin.get('request')
        
        info_sessin = request.session.get('data_template', {})
        id_files = info_sessin.get('idRequestFiles')
        cadena = id_files.strip('{}')
        valores = cadena.split(',')
        valores = [valor.strip().strip('}') for valor in valores]
        request_docs = valores
        
        datoSinFiltrar = request_docs[x]
        datoProceso = datoSinFiltrar.strip("[]'\"")
        
        print("datos al obtener el documentos")
        print(id_transaction)
        print(request_docs)
        ip = getIPOneshotAPI()
        url = ip + "/api/v1/document/" + str(id_transaction) + "/signed/" + datoProceso
        print(url)
                
        response = requests.get(url)

        ruta_carpeta = './media/oneshot/FilesFirmados/'
        
        ruta_archivo = os.path.join(ruta_carpeta, request_doc)
        with open(ruta_archivo, 'wb') as archivo:
            archivo.write(response.content)
        x+= 1

    return "Documentos Cargados"

def one_shot_Firmados(request):
    context_data = request.session.get('data_template', {})
    username = context_data.get('username')
    resultados = context_data.get('resultados')
    info_sessin = request.session.get('context_data', {})
    id_transaction = info_sessin.get('idRequest')
          
    return render(request, 'oneshot/one_shot_Done.html', {'username': username, 'resultados': resultados, 'request': id_transaction} )

def getDatetime():
    now = datetime.now()
    fecha_actual = [now.year, now.month, now.day, now.hour, now.minute, now]
    return fecha_actual

def sendCorreOperador(request):
        info_sessin = request.session.get('data_template', {})
        correo_electronico = info_sessin.get('email_operador')

        remitente = 'noreply@camaradecomercio.org.gt'  # Dirección de correo del remitente
        # remitente =  "jgaliano@ccg.gt"
        destinatario = correo_electronico #obtener correo de sesión del usuario
        asunto = "Confirmación de proceso de firmado"

        id_files = info_sessin.get('dpiUsuario')
        id_hash = info_sessin.get('idHash')
        
        user_name = info_sessin.get('username')
        url = 'http://localhost:8080/oneshot_done/?tsr=' + id_hash
        
        mensaje = user_name
        
        context = {
            'nombre': mensaje,
            'dpi': id_files,
            'data': url,
            'id': id
        }
            
        template_html = render_to_string('oneshot/one_shot_PlantillaCorreoOperador.html', context)
            
        try:
            send_mail(
                asunto,  # Asunto del correo
                '',  # Contenido del correo
                remitente,  # Correo del remitente
                [destinatario],  # Lista de destinatarios
                fail_silently=False,  # Si se establece en True, los errores no se levantarán sino que se registrarán en la consola
                html_message=template_html
            )
            return print("Correo enviado")
        except Exception as e:
            print(f"Error al enviar el correo: {e}")
    
def oneshot_done(request):
        data_id = request.GET.get('tsr')
        print(data_id)
        
        dataRequest = requestSign.objects.get(transaction_operador=data_id)
        cliente_ID = dataRequest.id_cliente_id
        dataCliente = cliente.objects.get(id=cliente_ID)
        
        fourNames = [dataCliente.primer_nombre, dataCliente.segundo_nombre, dataCliente.primer_apellido, dataCliente.segundo_apellido]
        fullName = ""
        
        for name in fourNames:
            fullName+= name + " "

        primer_nombre = fullName
        
        requestDoc = dataRequest.id_request
        dataDocs = documentos.objects.get(id_request=requestDoc)
        file_name = dataDocs.name_archivos
            
        info_document = []
        x = 0
        for nombre in file_name:
            x+= 1
            info_document.append([x, nombre, '310KB'])
                
        data_info = {
            'username': primer_nombre,
            'resultados': info_document
        }     
        return render(request, 'oneshot/one_shot_Done.html', data_info)

@login_required
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
def oneShot_solicitudes(request):
    if request.method == "GET":
        return render(request, 'oneshot/one_shot_solicitudes.html')
    else:
        
        search = cliente.objects.all()
        
        primerNombre = request.POST.get("inputName", "")
        segundoNombre = request.POST.get("inputSecondName", "")
        primerApellido = request.POST.get("inputApellido1", "")
        segundoApellido = request.POST.get("inputApellido2", "")
        dpi_user = request.POST.get("inputDPI", "")
        email_user = request.POST.get("inputEmail", "")
        fecha_inicio = request.POST.get("fechaIn")
        fecha_fin = request.POST.get("fechaEnd")
        estado_solicitud = request.POST.get("estatus_docs")
        
        if primerNombre:
            search = search.filter(primer_nombre__icontains=primerNombre)
        if segundoNombre:
            search = search.filter(segundo_nombre__icontains=segundoNombre)
        if primerApellido:
            search = search.filter(primer_apellido__icontains=primerApellido)
        if segundoApellido:
            search = search.filter(segundo_apellido__icontains=segundoApellido)
        if dpi_user:
            search = search.filter(dpi__icontains=dpi_user)
        if email_user:
            search = search.filter(email__icontains=email_user)
        
        search = search.prefetch_related('cliente')
        
        context = {
            'solicitudes': search
        }
        
        return render(request, 'oneshot/one_shot_solicitudes.html', context)

@login_required 
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')  
def busquedaOperados(request, requestID):
    if request.method == 'GET':
        
        dataCliente = cliente.objects.get(id=requestID)
        
        fullName = dataCliente.primer_nombre + " " + dataCliente.segundo_nombre + " " + dataCliente.primer_apellido + " " + dataCliente.segundo_apellido
        
        dataRequest = requestSign.objects.get(id_cliente_id = requestID)
            
        dataVideo = dataCliente.tipo
        statusDocumentos = dataCliente.status
        
        if dataRequest.id_video == "None":
            
            dataDocumentos = documentos.objects.get(id_request=dataRequest.id_request)
            
            listDocuments = dataDocumentos.name_archivos
            viewDocuments = []
            for nombre in listDocuments:
                viewDocuments.append([nombre, '310KB'])
            
            contexto = {
                'username': fullName,
                'documentos': viewDocuments,
                'video': dataVideo,
                'status': statusDocumentos
            }
            return render(request, 'oneshot/one_shot_vistaBusqueda.html', contexto)    
        else:
            
            context_data = {
                'correo': dataCliente.email, 
                'idRequest': dataRequest.id_request,
                'name': dataCliente.primer_nombre,
                'name2': dataCliente.segundo_nombre,
                'apellido1': dataCliente.primer_apellido,
                'apellido2': dataCliente.segundo_apellido,
                'dpi': dataCliente.dpi,
                'email': dataCliente.email,
                'celular': dataCliente.celular,
                'address': dataCliente.direccion
            }
            request.session['context_data'] = context_data
            
            # dataDocumentos = documentos.objects.get(id_request=dataRequest.id_request)
            
            # if dataDocumentos:
            #     listDocuments = dataDocumentos.name_archivos
            #     viewDocuments = []
            #     for nombre in listDocuments:
            #         viewDocuments.append([nombre, '310KB'])
                    
            try:
                dataDocumentos = documentos.objects.get(id_request=dataRequest.id_request)
                listDocuments = dataDocumentos.name_archivos
                viewDocuments = []
                for nombre in listDocuments:
                    viewDocuments.append([nombre, '310KB'])
            except documentos.DoesNotExist:
                # Manejo de la excepción cuando no se encuentra el documento
                viewDocuments = []
            
            contexto = {
                'username': fullName,
                'video': dataVideo,
                'documentos': viewDocuments,
                'status': statusDocumentos,
                'request': dataRequest.id_request,
                'nombre1': dataCliente.primer_nombre,
                'nombre2': dataCliente.segundo_nombre,
                'apellido1': dataCliente.primer_apellido,
                'apellido2': dataCliente.segundo_apellido,
                'email': dataCliente.email,
                'celular': dataCliente.celular,
                'direccion': dataCliente.direccion,
                'dpi': dataCliente.dpi 
            }
            return render(request, 'oneshot/one_shot_busquesda_Video.html', contexto)
   
    else:
        
        requestInput = request.POST['requestIdOneshot']
        
        url = "http://10.10.10.9:8084/api/v1/videoid/" + str(requestInput) + "/validate"

        payload = json.dumps({
            "token": "118336d4c91b4aca8a53bee8f18fd044",
            "username": "1108124",
            "password": "29yqdGGw",
            "pin": "belorado74",
            "rao": "98"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, data=payload)
        dataValidate = json.loads(response.text)
        print(dataValidate)
        statusValidate = dataValidate.get('status')
        print(statusValidate)
        
        dataRequest = requestSign.objects.get(id_request = requestInput)
        idRequest = dataRequest.id_cliente_id
        if dataRequest.aprovado == "No":
            if statusValidate == "500 Internal Server Error":
                newUrl = "/oneshot/busquedaOperados/" + str(idRequest)
                reasonError = "Video identificación pendiente de realizar, para validar la solicitud es necesario que la video identifición haya sido realizada"
                messages.error(request, reasonError)
                return redirect(newUrl)
            else:
                dataRequest.aprovado = "Si"
                dataRequest.save()
                newURL = "/oneshot/aprobarVideo/" + str(requestInput)
                return redirect(newURL)
        else: 
            dataRequest.aprovado = "Si"
            dataRequest.save()
            newURL = "/oneshot/aprobarVideo/" + str(requestInput)
            return redirect(newURL)

def sendOtpOneShot(request):
    numero = request.GET.get('numero')
    ip = getIPOneshotAPI()
    url = ip + "/api/v1/otp/" + str(numero)

    payload = json.dumps({
        "delivery_method": "whatsapp"
    })
        
    headers = {
        'Content-Type': 'application/json'
    }
        
    response = requests.request("POST", url, headers=headers, data=payload)
    return response


def aprobarOneshot(request, requestID):
    return redirect('aprobarOneshot')
    
@login_required
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
def validarInfo(request, requestID):
    dataRequest = requestSign.objects.get(id_request=requestID)
    dataCliente = cliente.objects.get(id=dataRequest.id_cliente_id)
    contexto = {
        'nombre1': dataCliente.primer_nombre,
        'nombre2': dataCliente.segundo_nombre,
        'apellido1': dataCliente.primer_apellido,
        'apellido2': dataCliente.segundo_apellido,
        'dpi': dataCliente.dpi,
        'celular': dataCliente.celular,
        'direccion': dataCliente.direccion,
        'email': dataCliente.email
    }
    
    if request.method == "POST":
        
        response = validarRequestOneshot(requestID)
        dataAprove = json.loads(response.text)
        statusAprove = dataAprove.get('status')
        
        if statusAprove == "500 Internal Server Error":            
            newURL = "/oneshot/aprobarVideo/" + str(requestID)
            reasonError = "Video Identificación No Realizada"
            messages.error(request, reasonError)            
            return redirect(newURL)
        else:
            # Obtener Scratchcard de request oneshot
            ip = getIPOneshotAPI()
            url = ip + "/api/v1/request/" + str(requestID)
            response = requests.request("GET", url)
            getDataRequest = json.loads(response.text)
            getScratchcard = getDataRequest.get('details', None).get('scratchcard', None)

            # Sobre escribir información capturada por OCR   
            
            newPhoneNumber = "+502" + str(dataCliente.celular)
                     
            payload = json.dumps({
                "scratchcard": getScratchcard,
                "given_name": dataCliente.primer_nombre + dataCliente.segundo_nombre,
                "surname_1": dataCliente.primer_apellido,
                "surname_2": dataCliente.segundo_apellido,
                "serial_number": dataCliente.dpi,
                "profile": "CCPNIndividual",
                "email": dataCliente.email,
                "country_name": "GT",
                "mobile_phone_number": newPhoneNumber,
                "registration_authority": "98"
            })

            response = requests.request("PUT", url, data=payload)

            print(response.text)
            return redirect('one_shot_docs')

    return render(request, 'oneshot/validarInformacion.html', contexto)


def validarRequestOneshot(idRequest):
    ip = getIPOneshotAPI()
    url = ip + "/api/v1/request/" + str(idRequest) + "/approve"
        
    payload = json.dumps({
        "token": "118336d4c91b4aca8a53bee8f18fd044",
        "username": "1108124",
        "password": "29yqdGGw",
        "pin": "belorado74",
        "rao": "98"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, data=payload)
    return response
