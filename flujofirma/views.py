from pathlib import Path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from . models import Firmante, Envio, Imagen, DatosFirmante, ArchivosPDF, documentos, uploadDocument, VideoIdentificacion, detalleFirma, log_oneshot, VitacoraFirmado
from signbox.models import billingSignboxSandbox, billingSignboxProd, signboxAPI
from django.views.decorators.csrf import csrf_exempt
import secrets
import json
import re
import random
from django.core.mail import send_mail
import requests
from django.template.loader import render_to_string
from webhook.models import webhookIP
from django.views.defaults import server_error
import time
from io import BytesIO
import tempfile
import os
from django.core.files.base import ContentFile
from app.models import LicenciasSistema, UsuarioSistema, PerfilSistema, token_oneshot
from oneshot.models import oneshotAPI
from django.utils import timezone

# from requests.packages.urllib3.exceptions import InsecureRequestWarning

# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def is_mobile(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    # Expresión regular para detectar dispositivos móviles
    mobile_regex = re.compile(r"android|iphone|ipod|blackberry|windows phone", re.I)
    
    if mobile_regex.search(user_agent):
        return True
    return False

@csrf_exempt
def helloworld(request):
    if is_mobile(request):
        return render(request, 'flujofirma/is_mobile.html')
    else:
        if request.method == "POST":
            try:
                positions = json.loads(request.POST.get('positions'))
                print(positions)
                return redirect('/flujo_firma/confirmacion_envio/')
            except json.JSONDecodeError:
                return JsonResponse({'status': 'error', 'message': 'Error al decodificar los datos JSON.'})
        else: 
            pdf_files = [
                "https://signgo-bucket.s3.amazonaws.com/media/signbox/FilesNoFirmados/555076121812300/Prueba_6.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA45XFJQA2SMB73TVY%2F20241221%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20241221T181836Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=3df120f4db4c4c245fac604d06c81b8fd871e52a87b098b22a7db10f51845580",
                "https://signgo-bucket.s3.amazonaws.com/media/signbox/FilesNoFirmados/555076121812300/Prueba_7.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA45XFJQA2SMB73TVY%2F20241221%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20241221T181836Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=99034771bd24953578bc4d6b194dfffe5bc8c99b41ee814ea3ce71224e4223ad",
            ]

            # Lista de firmantes
            firmantes = [
                {"name": "Jhonatan Galiano", "id": "1"},
                {"name": "Danny Marroquin", "id": "2"},
                {"name": "Josue Lopez", "id": "3"},
                {"name": "Hector Morales", "id": "4"},
                {"name": "Norman Sinay", "id": "5"},
            ]

            return render(request, 'prueba.html', {'pdf_files': pdf_files, 'firmantes': firmantes})

@login_required
def crear_flujo(request):
    if request.method == 'POST':
        try:
            # Obtener datos del envío
            nombre_envio = request.POST['nombreEnvio']
            flujo_por_orden = request.POST.get('flujoPorOrden') is None

            # Validar que el nombre del envío no esté vacío
            if not nombre_envio:
                messages.error(request, "El nombre del envío es obligatorio.")
                return redirect('/flujo_firma/crear_flujo/')
            
            tokenEnvio = secrets.token_urlsafe(50)

            # Crear el envío
            envio = Envio.objects.create(
                nombre_envio=nombre_envio,
                flujo_por_orden=flujo_por_orden,
                TokenAuth=tokenEnvio
            )

            orden_envio = 1
            # Procesar los firmantes
            firmantes_data = []
            for key in request.POST.keys():
                tokenFirmante = secrets.token_urlsafe(50)
                if key.startswith('firmanteCorreo_'):
                    suffix = key.split('_')[1]
                    correo = request.POST.get(f'firmanteCorreo_{suffix}', '').strip()
                    nombres = request.POST.get(f'firmanteNombres_{suffix}', '').strip()
                    apellidos = request.POST.get(f'firmanteApellidos_{suffix}', '').strip()
                    tipo_firma = request.POST.get(f'firmanteTipoFirma_{suffix}', '').strip()

                    # Validar campos obligatorios
                    if correo and nombres and apellidos and tipo_firma:
                        firmantes_data.append(Firmante(
                            envio=envio,
                            correo=correo,
                            nombres=nombres,
                            apellidos=apellidos,
                            tipo_firma=tipo_firma,
                            TokenAuth=tokenFirmante, 
                            orden_flujo=int(orden_envio)
                        ))
                        orden_envio+= 1
                

            firmantes_guardados = Firmante.objects.bulk_create(firmantes_data)
            
            validarFlujo = validar_flujo(tokenEnvio)
            return redirect(validarFlujo)
            
        except Exception as e:
            messages.error(request, f'Error al guardar firmantes: {e}')
            return redirect('/flujo_firma/crear_flujo/')
    else:
        
        validate_licencia = validación_licencia(request.user.id)
        validate_licencia_parse = json.loads(validate_licencia)
        reason_error = None

        if validate_licencia_parse['success']:
            estado = "activa"
        else:
            if validate_licencia_parse['error'] == 'Creditos Agotados':
                messages.error(request, validate_licencia_parse['error'])
                estado = "creditos"
            elif validate_licencia_parse['error'] == 'No se ha podido encontrar su licencia':
                messages.error(request, validate_licencia_parse['error'])
                estado = "404"
            else:
                messages.error(request, validate_licencia_parse['error'])
                estado = "expirada"
        
        contexto = {
            'licencia': estado        
        }
    
        return render(request, 'flujofirma/crear_flujo.html', contexto)

@login_required
def datos_firmantes(request, tokenFirmante):
    try:
        find_firmante = Firmante.objects.get(TokenAuth=tokenFirmante)
    except Exception as e:
        return render(request, 'AccesoDenegado.html')
    if request.method == 'POST':
        try: 
            imagen_frontal = request.FILES.get('imagenFrontal')
            imagen_posterior = request.FILES.get('imagenLateral')
            imagen_persona = request.FILES.get('imagenConDpi')
            oneshot_video = request.POST.get('oneshotVideoCheckbox', 'off') == 'on'
            
            dpi_persona = request.POST['dpi_persona']
            celular_persona = request.POST['celular_persona']
            direccion_persona = request.POST['dir_persona']
            
            datos_firmante = DatosFirmante(
                dpi = dpi_persona,
                celular = celular_persona,
                direccion = direccion_persona,
                with_video = oneshot_video,
                Firmante = find_firmante
            )
            
            if imagen_frontal and imagen_posterior and imagen_persona:
                base_path = 'media/oneshot/firmantes/img/'
                folder_name = f'img_{find_firmante.pk}'
                
                if imagen_frontal:
                    datos_firmante.imagen_dpi_frontal = guardar_imagen(imagen_frontal, base_path, folder_name, find_firmante)
                
                if imagen_posterior:
                    datos_firmante.imagen_dpi_posterior = guardar_imagen(imagen_posterior, base_path, folder_name, find_firmante)
                    
                if imagen_persona:
                    datos_firmante.imagen_persona = guardar_imagen(imagen_persona, base_path, folder_name, find_firmante)
                
                
            datos_firmante.save()         
            
            find_firmante.Datos = True
            find_firmante.save()
            validarFlujo = validar_flujo(find_firmante.envio.TokenAuth)
            return redirect(validarFlujo)
        except Exception as e:
            messages.error(request, f'Error al guardar la información: {e}')
            redirect(f'/flujo_firma/datos_firmante/{tokenFirmante}')
    else:
        
        contexto = {
            'datos_firmante': find_firmante
        }
        return render(request, 'flujofirma/datos_firmantes.html', contexto)

@login_required
def progreso_flujo(request, tokenEnvio):
    find_envio = Envio.objects.get(TokenAuth=tokenEnvio)
    find_firmantes = Firmante.objects.filter(envio=find_envio).order_by('id')
    find_documentos = uploadDocument.objects.filter(envio=find_envio.TokenAuth)
    
    firmantes = [
        {"nombres": firmante.nombres, "estado": str(firmante.is_firmado)}
        for firmante in find_firmantes
    ]
    
    print(firmantes)
    
    contexto = {
        'firmantes_find': firmantes,
        'lista_firmantes': find_firmantes,
        'documentos': find_documentos
    }
    
    return render(request, 'flujofirma/progreso_flujo.html', contexto)

@login_required
def confirmacion_envio_flujo(request, tokenEnvio):
    if request.method == "GET":
        try:
            find_envio = Envio.objects.get(TokenAuth=tokenEnvio)
            find_firmantes = Firmante.objects.filter(envio=find_envio).order_by('id')
            find_firmantes_cantidad = Firmante.objects.filter(envio=find_envio).count()
            
            # DESCONTAR CREDITOS SI LA LICENCIA ES INDIVIDUAL
            usuario_firmante = UsuarioSistema.objects.get(UsuarioGeneral=request.user.id)
            licencia_usuario = LicenciasSistema.objects.filter(usuario=usuario_firmante.pk, tipo='FF_Oneshot').last()
            licencia_usuario.consumo = licencia_usuario.consumo + int(find_firmantes_cantidad)
            licencia_usuario.save()
                        
            if find_envio.flujo_por_orden == True:
                ordenado = True
            else: 
                ordenado = False
            
            contexto = {
                'firmantes': find_firmantes, 
                'TokenAuth': tokenEnvio,
                "Orden": ordenado 
            }
        except Exception as e:
            return render(request, 'AccesoDenegado.html')
    return render(request, 'flujofirma/confirmacion_envio_flujo.html', contexto)

def validar_flujo(tokenEnvio):
    # Valida si hay OneShots
    # Valida si se ingresó la información de todos los usuarios
    # Redirige al siguiente en la lista si es necesario
    try:
        find_token_envio = Envio.objects.get(TokenAuth=tokenEnvio)
        find_oneshot = Firmante.objects.filter(tipo_firma='oneshot', envio=find_token_envio.pk).count()
        find_data_oneshot = Firmante.objects.filter(Datos=True, envio=find_token_envio.pk).count()
        find_data_oneshot_pending = Firmante.objects.filter(tipo_firma='oneshot', Datos=False, envio=find_token_envio.pk).first()
        print(find_data_oneshot)
        
        if find_oneshot >= 1 and find_oneshot != find_data_oneshot:
            return f'/flujo_firma/datos_firmante/{find_data_oneshot_pending.TokenAuth}'
        else:
            return f'/flujo_firma/upload_files/{tokenEnvio}'
    except Exception as e:
        print(f'Error:{e}')
        messages.error( f"No se puede validar el flujo: {e}")
        return '/flujo_firma/crear_flujo/'
        
    

def guardar_imagen(archivo, base_path, folder_name, Usuario):
    try:
        nueva_imagen = Imagen()
        nueva_imagen.set_upload_paths(base_path, folder_name)
        nueva_imagen.imagen = archivo
        nueva_imagen.UsuarioFirmante = Usuario
        nueva_imagen.save()
        presigned_url = nueva_imagen.get_presigned_url()
        nueva_imagen.presigned_url = presigned_url
        nueva_imagen.save()
        return nueva_imagen
    except Exception as e:
        print(e)
        messages.error(f'Error al guardar imagen: {e}')
        return e

@login_required
def upload_files(request, tokenEnvio):
    if request.method == "POST":
        nombre_archivos = []
        pdf_files = request.FILES.getlist('pdf_files')
        
        nombreCarpeta = random.randint(100000000000000, 999999999999999) 
        base_path = 'media/flujofirma/FilesNoFirmados/'
        urls = []

        for pdf_file in pdf_files:
            nueva_archivo = ArchivosPDF()
            nombre_inicial = pdf_file.name
            nombre_archivos.append(nombre_inicial)
            nueva_archivo.set_upload_paths(base_path, nombreCarpeta)
            nueva_archivo.archivo = pdf_file
            nueva_archivo.save()
            presigned_url = nueva_archivo.get_presigned_url()
            urls.append(presigned_url)
            
            insertDocument = uploadDocument(
                nombre_documento = nombre_inicial,
                url_documento = presigned_url,
                envio = tokenEnvio
            )
            insertDocument.save()    
            
                        
        tokenDocumentos = secrets.token_urlsafe(25)
        requestDocumentos = documentos(
            status="NoFirmado",
            secret=tokenDocumentos,
            nameArchivos=nombre_archivos,
            url_archivos=urls,
            nameCarpeta=str(nombreCarpeta),
            tokenEnvio=tokenEnvio
        )
        requestDocumentos.save()    
        newURL = "/flujo_firma/asignar_firma/" + tokenEnvio
        return redirect(newURL)
    return render(request, "flujofirma/upload_files.html")


@login_required
def asignar_firma(request, tokenEnvio):
    if is_mobile(request):
        return render(request, 'flujofirma/is_mobile.html')
    else:
        if request.method == "POST":
            try:
                positions = json.loads(request.POST.get('positions'))                
                
                for position in positions:
                    firmante_id = position.get('firmante_id')
                    document_url = position.get('document_url')
                    document_name = position.get('document_name')
                    page = position.get('page')
                    x = position.get('x')
                    y = position.get('y')
                    
                    getEnvio = Envio.objects.get(TokenAuth=tokenEnvio)
                    getFirmante = Firmante.objects.get(id=firmante_id)
                    getDocumento = uploadDocument.objects.get(url_documento=document_url)
                    
                    getX1 = convertir_x(int(x))
                    getX2 = int(getX1) + 170
                    getY1 = convertir_y(int(y))
                    getY2 = int(getY1) + 50
                    
                    parseX1 = int(getX1) - 20
                    parseX2 = int(getX2) - 20
                    parseY1 = int(getY1) + 20
                    parseY2 = int(getY2) + 20
                    
                    insertFirmas = detalleFirma(
                        envio = getEnvio,
                        firmante = getFirmante,
                        documento = getDocumento,
                        pagina = str(int(page) - 1),
                        p_x1 = str(parseX1),
                        p_x2 = str(parseX2),
                        p_y1 = str(parseY1),
                        p_y2 = str(parseY2)
                    )   
                    insertFirmas.save()
                    
                    # Generar Solicitudes APIs
                    if getEnvio.flujo_por_orden == True:
                        result = envio_ordenado(tokenEnvio)
                        parse_result = json.loads(result)
                    else:
                        result = envio_masivo(tokenEnvio)
                        parse_result = json.loads(result)
                    
                    if parse_result["success"]:
                        None   
                    else:
                        messages.error(request, f'Error al guardar datos de firmante: {str(parse_result["error"])}')
                        return redirect(f'/flujo_firma/crear_flujo/')
                                                   
                
                return redirect(f'/flujo_firma/confirmacion_envio/{tokenEnvio}')
            except Exception as e:
                messages.error(request, f'Error al guardar datos de firmante: {e}')
                return redirect(f'/flujo_firma/crear_flujo/')
        else: 
            try:
                
                url_documentos = []
                find_documents = documentos.objects.get(tokenEnvio=tokenEnvio)
                for documento in find_documents.url_archivos:
                    url_documentos.append(documento)
                    
                
                firmantes = []
                find_envio = Envio.objects.get(TokenAuth=tokenEnvio)
                find_firmantes = Firmante.objects.filter(envio=find_envio.id)
                for id_firmantes in find_firmantes:
                    firmantes.append({
                        "name": f"{id_firmantes.nombres} {id_firmantes.apellidos}",
                        "id": str(id_firmantes.pk)
                    })
                    
                contexto = {
                    'pdf_files': url_documentos, 
                    'firmantes': firmantes,
                    'tokenEnvio': tokenEnvio
                }

                return render(request, 'flujofirma/asociar_firma.html', contexto)
            except Exception as e:
                print("5")
                messages.error(request, f'Error al cargar documentos: {e}')
                return redirect(f'/flujo_firma/asignar_firma/{tokenEnvio}')
            


def convertir_x(x_obt):
    a_x = 0.84
    b_x = 1.6
    return round(a_x * x_obt + b_x)

def convertir_y(y_obt):
    a_y = 0.825
    b_y = -78.725
    return round(a_y * y_obt + b_y)

def envio_masivo(tokenEnvio):
    try:
        find_envio = Envio.objects.get(TokenAuth=tokenEnvio)
        find_firmantes = Firmante.objects.filter(envio=find_envio)
        
        errors = []
        success = []
        parse_result_correo = None
        
        for firmante in find_firmantes:
            if firmante.tipo_firma == "oneshot" and firmante.is_enviado == False:
                result = validate_one_shot(firmante.pk)
                parse_result = json.loads(result)
                if parse_result["success"]:
                    data_result = json.loads(parse_result["data"])
                    if data_result["status"] == "201 Created" or "200 OK":
                        if parse_result["Correo"]:
                            result_correo = enviar_correo("Solicitud de firma One-Shot", "Por favor firmar el siguiente enlace", "notificaciones@signgo.com.gt", firmante.correo, firmante.TokenAuth)
                            parse_result_correo = json.loads(result_correo)
                            
                        if (parse_result_correo and parse_result_correo.get("success")) or parse_result["Correo"] == False:
                            # success.append({'firmante': firmante.pk, 'details': str(data_result["details"]["request_pk"])})
                            firmante.is_enviado = True
                            firmante.fecha_enviado = timezone.now()
                        else:
                            # errors.append({'firmante': firmante, 'details': str(data_result["details"])})
                            None
                    else: 
                        # errors.append({'firmante': firmante, 'details': str(data_result["details"])})
                        None
                else:
                    return json.dumps({"success": False, "error": str(parse_result["error"])})
            elif firmante.tipo_firma == "larga" and firmante.is_enviado == False:
                result = generate_signbox(firmante.pk)
                parse_result = json.loads(result)
                
                if parse_result["success"]:
                    firmante.is_enviado = True
                    firmante.fecha_enviado = timezone.now()
                else:
                    None
                
            firmante.save()
        
        return json.dumps({"success": True, "data": "True"})
    except Exception as e:
        print(f'envio masivo: {e}')
        return json.dumps({"success": False, "error": f'envio_masivo: {str(e)}'})

def envio_ordenado(tokenEnvio):
    try:
        find_envio = Envio.objects.get(TokenAuth=tokenEnvio)
        firmante = Firmante.objects.filter(envio=find_envio,is_enviado=False).first()
        find_enviado = Firmante.objects.filter(envio=find_envio, is_enviado=True, is_firmado=False).exists()
        
        parse_result_correo = None
        
        if find_enviado == False:        
            if firmante.tipo_firma == "oneshot" and firmante.is_enviado == False:
                result = validate_one_shot(firmante.pk)
                parse_result = json.loads(result)
                if parse_result["success"]:
                    data_result = json.loads(parse_result["data"])
                    if data_result["status"] == "201 Created" or "200 OK":
                        if parse_result["Correo"]:
                            result_correo = enviar_correo("Solicitud de firma One-Shot", "Por favor firmar el siguiente enlace", "notificaciones@signgo.com.gt", firmante.correo, firmante.TokenAuth)
                            parse_result_correo = json.loads(result_correo)
                                
                        if (parse_result_correo and parse_result_correo.get("success")) or parse_result["Correo"] == False:
                            # success.append({'firmante': firmante.pk, 'details': str(data_result["details"]["request_pk"])})
                            firmante.is_enviado = True
                            firmante.fecha_enviado = timezone.now()
                        else:
                            # errors.append({'firmante': firmante, 'details': str(data_result["details"])})
                            None
                    else: 
                        # errors.append({'firmante': firmante, 'details': str(data_result["details"])})
                        None
                else:
                    return json.dumps({"success": False, "error": str(parse_result["error"])})
            elif firmante.tipo_firma == "larga" and firmante.is_enviado == False:
                result = generate_signbox(firmante.pk)
                parse_result = json.loads(result)
                    
                if parse_result["success"]:
                    firmante.is_enviado = True
                    firmante.fecha_enviado = timezone.now()
                else:
                    None
                    
            firmante.save()
        else: 
            None
        
        return json.dumps({"success": True, "data": True})
    except Exception as e:
        print(e)
        return json.dumps({"success": False, "error": str(e)})

def validate_one_shot(idFirmante):
    try:
        find_oneshot = Firmante.objects.get(pk=idFirmante)
        find_datos_firmante = DatosFirmante.objects.get(Firmante=find_oneshot)
        if find_datos_firmante.with_video:
            result = generate_video_id_oneshot(idFirmante)
            parse_result = json.loads(result)
            try:
                if parse_result["success"]:
                    return json.dumps({"success": True, "data": parse_result["data"], "Correo": False})
                else:
                    return json.dumps({"success": False, "error": str(parse_result["error"]), "Correo": False})
            except Exception as e:
                print(f"error: data_validate_oneshot: {e}")
                return json.dumps({"success": False, "error": f'validate_oneshot: {str(e)}'})
        else:
            result = generate_simple_oneshot(idFirmante)
            parse_result = json.loads(result)
            try:
                if parse_result["success"]:
                    return json.dumps({"success": True, "data": parse_result["data"], "Correo": True})
                else:
                    return json.dumps({"success": False, "error": str(parse_result["error"])})
            except Exception as e:
                print(f"error: data_validate_oneshot: {e}")
                return json.dumps({"success": False, "error": f'validate_oneshot: {str(e)}'})
    except Exception as e:
        print(f'validate oneshot: {e}')
        return json.dumps({"success": False, "error": f'validate_oneshot: {str(e)}'})

def generate_simple_oneshot(idFirmante):
    try:

        protocolo, ip = validar_API_oneshot()
        
        firmante_oneshot = Firmante.objects.get(pk=idFirmante)
        datos_firmante = DatosFirmante.objects.get(Firmante=firmante_oneshot)
        
        username_operador = '1108124'
        password_operador = '29yqdGGw'
        pin_operador = 'belorado74'
        
        billing_username = 'ccg@ccg'
        billing_password = 'dDJHOVQ3MU8='
        
        url_API = f'{protocolo}://{ip}/api/v1/request'
        
        env = 'sandbox'
        
        payload={
            'given_name': firmante_oneshot.nombres,
            'surname_1': firmante_oneshot.apellidos,
            'surname_2': "",
            'id_document_type': 'IDC',
            'id_document_country': 'GT',
            'serial_number': datos_firmante.dpi,
            'email': firmante_oneshot.correo,
            'mobile_phone_number': f'+502{datos_firmante.celular}',
            'registration_authority': '98',
            'profile': 'CCPNIndividual',
            'username': username_operador,
            'password': password_operador,
            'pin': pin_operador,
            'env': env,
            'billing_username': billing_username,
            'billing_password': billing_password,
            'residence_city': 'Guatemala',
            'residence_address': datos_firmante.direccion
            }
        
        payload_json = json.dumps(payload)

        files = {
            'document_front': ('img_front.jpg', datos_firmante.imagen_dpi_frontal.imagen, 'image/jpg'),
            'document_rear': ('img_rear.jpg', datos_firmante.imagen_dpi_posterior.imagen, 'image/jpg'),
            'document_owner': ('img_owner.jpg', datos_firmante.imagen_persona.imagen, 'image/jpg')
        }

        response = requests.post(url_API, data=payload, files=files)
        result = json.loads(response.text)
        
        insert_log = log_oneshot(
            log=response.text,
            Firmante=firmante_oneshot,
            status = str(result["status"]),
            detail = str(result["details"]) 
        )
        insert_log.save()
        
        return json.dumps({"success": True, "data": response.text})
    except Exception as e:
        print(f"error generate_simple_oneshot: {e}")
        return json.dumps({"success": False, "error": f'generate_simple_oneshot: {str(e)}'})

def generate_video_id_oneshot(idFirmante):
    try:
        
        firmante_oneshot = Firmante.objects.get(pk=idFirmante)
        datos_firmante = DatosFirmante.objects.get(Firmante=firmante_oneshot)
        
        username_operador = '1108124'
        password_operador = '29yqdGGw'
        pin_operador = 'belorado74'
        
        billing_username = 'ccg@ccg'
        billing_password = 'dDJHOVQ3MU8='
        
        protocolo, ip = validar_API_oneshot()
        
        url_API = f'{protocolo}://{ip}/api/v1/videoid'
        
        env = 'sandbox'

        payload = json.dumps({
            "username": username_operador,
            "password": password_operador,
            "pin": pin_operador,
            "mobile_phone_number": f"+502{datos_firmante.celular}",
            "email": firmante_oneshot.correo,
            "registration_authority": "98",
            "profile": "CCPNIndividual",
            "residence_city": "Guatemala",
            "residence_address": datos_firmante.direccion,
            "videoid_mode": 1,
            "billing_username": billing_username,
            "billing_password": billing_password,
            "env": env,
            "token": "118336d4c91b4aca8a53bee8f18fd044",
            "given_name": firmante_oneshot.nombres,
            "surname_1": firmante_oneshot.apellidos,
            "surname_2": ""
        })
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url_API, data=payload)
        result = json.loads(response.text)
        
        insert_log = log_oneshot(
            log=response.text,
            Firmante=firmante_oneshot,
            status = str(result["status"]),
            detail = str(result["details"]["request_pk"]) 
        )
        insert_log.save()
        
        return json.dumps({"success": True, "data": response.text})
    except Exception as e:
        return json.dumps({"success": False, "error": e})

def generate_signbox(idFirmante):
    firmante_signbox = Firmante.objects.get(pk=idFirmante)
    result = enviar_correo("Solicitud de Firma Electrónica", "Firme el siguiente documento con su certificado de larga duración", "notificaciones@signgo.com.gt", firmante_signbox.correo, firmante_signbox.TokenAuth)
    parse_result = json.loads(result)
    
    if parse_result["success"]:
        return json.dumps({"success": True, "data": "ok"})
    else: 
        return json.dumps({"success": False, "error": str(parse_result["error"])})        

def enviar_correo(asunto_mail, mensaje_mail, remitente_mail, destinatario_mail, ad1):
    try:
        
        find_firmante = Firmante.objects.get(TokenAuth=ad1)
        getIpDominio = webhookIP.objects.get(id=1)
        
        protocolo = 'http' if getIpDominio.protocol == "0" else 'https'
        
        url = f'https://signgo.com.gt/flujo_firma/validar_documento/{find_firmante.TokenAuth}'
        
        context = {
            'data': url,
            'nombre': f'{find_firmante.nombres} {find_firmante.apellidos}',
            'asunto': asunto_mail
        }
        
        template_html = render_to_string('flujofirma/plantilla_correo.html', context)
        
        
        destinatarios = [destinatario_mail]
        send_mail(asunto_mail, '', remitente_mail, destinatarios, fail_silently=False, html_message=template_html)
        return json.dumps({"success": True, "data": "Enviado"})
    except Exception as e:
        print(f'send_mail: {e}')
        return json.dumps({"success": False, "error": f'send_mail: {str(e)}'})
    
def validar_documento(request, tokenFirmante):
    try:
        find_firmante = Firmante.objects.get(TokenAuth=tokenFirmante)
        print(find_firmante.is_firmado)
        if find_firmante.is_firmado == False:
        
            if find_firmante.tipo_firma == 'larga':      
                dataDocuments = detalleFirma.objects.filter(firmante=find_firmante).order_by('id')

                viewDocuments = []
                for documento in dataDocuments:
                    viewDocuments.append([documento.documento.nombre_documento, '310KB', documento.documento.url_documento])
                    
                type_device = is_mobile(request)
                
                contexto = {
                    'firmante': find_firmante,
                    'documentos': viewDocuments,
                    'tokenFirmante': tokenFirmante,
                    'is_mobile': type_device
                }
                
                return render(request, 'flujofirma/validar_documento_signbox.html', contexto)
            else:
                
                dataDocuments = detalleFirma.objects.filter(firmante=find_firmante).order_by('id')
                find_request = log_oneshot.objects.get(Firmante=find_firmante.pk)

                viewDocuments = []
                for documento in dataDocuments:
                    viewDocuments.append([documento.documento.nombre_documento, '310KB', documento.documento.url_documento])
                
                contexto = {
                    'firmante': find_firmante,
                    'documentos': viewDocuments,
                    'tokenFirmante': tokenFirmante,
                    'TokenRequest': find_request.detail
                }
                
                
                return render(request, 'flujofirma/validar_documento_oneshot.html', contexto)
        else:
            contexto = {
                
            }
            return render(request, 'flujofirma/redireccion_firmado.html', contexto)
    except Exception as e:
        print(e)
        return server_error(request)

def firmar_documento_cld(request, tokenFirmante):
    if request.method == "POST":
        new_url = f'/flujo_firma/validar_documento/{tokenFirmante}'
        try:
            usuarioCliente = request.POST.get('inputUsuario')
            contraseña = request.POST.get('inputContraseña')
            pin = request.POST.get('inputPin')          
            
            validatePin = verifyPin(usuarioCliente, contraseña, pin)
            
            find_firmante = Firmante.objects.get(TokenAuth=tokenFirmante)
            dataDocuments = detalleFirma.objects.filter(firmante=find_firmante).order_by('id')
            
            idsAPI = []
            idError = []
            idOK = []
            
            if validatePin == None:
            
                for document in dataDocuments:
                    tokenArchivo = secrets.token_urlsafe(50)
                    coordenadas = f'{document.p_x1},{document.p_y1},{document.p_x2},{document.p_y2}'
                    print(coordenadas)
                    idFirma = signDocument("nada", usuarioCliente, contraseña, pin, document.documento.nombre_documento, coordenadas, document.pagina, tokenArchivo, ", carpeta me parece", document.documento.url_documento)
                    parse_idFirma = json.loads(idFirma)
                    
                    if parse_idFirma["success"] == True:
                        idFirma = parse_idFirma["data"]
                    else:
                        idFirma = parse_idFirma["error"]
                        
                    saveIDFile(document.documento.nombre_documento, tokenArchivo, document.envio.pk, "Pendiente", tokenFirmante, idFirma, document.documento.pk) # cambié el user id del firmante por el token del firmante
                    idsAPI.append(idFirma)
                    print(idFirma)   
                    time.sleep(1)
                
                # Validación de proceso de firmado
                while True:
                    registros_pendientes = VitacoraFirmado.objects.filter(IDArchivoAPI__in=idsAPI, EstadoFirma='Pendiente')
                     
                    if not registros_pendientes.exists():
                        print("Todos los estados han cambiado.")
                        break
                
                    time.sleep(1)
                    
                # Validación de logs de firmado
                for id in idsAPI:
                    validateID = VitacoraFirmado.objects.get(IDArchivoAPI=id)
                    idOK.append(id) if validateID.EstadoFirma == "Firmado" else idError.append(id)
                    
                if idOK:
                    
                    if find_firmante.envio.flujo_por_orden == True:
                        result = envio_ordenado(find_firmante.envio.TokenAuth)
                    else:
                        result = envio_masivo(find_firmante.envio.TokenAuth)  
                    
                    url_sign = "/flujo_firma/firmado/" + tokenFirmante
                    return redirect(url_sign)
                else:
                    messages.error(request, 'Error al Firmar. Por favor intentelo mas tarde.')
                    return redirect(new_url)
                
            
        except Exception as e:
            print(f'Error: {e}')
      
        
        reasonError = translateResponse(validatePin)
        messages.error(request, reasonError)
        return redirect(new_url) 

    else:
        return server_error(request)
        
@login_required
def aprobacion_video_id_oneshot_temporal(request):
    
    if request.method == 'POST':
        video_id = request.POST['video_id']
        status = 'VIDEOPENDING'
        previous_status = 'VIDEOPENDING'
        request_video = video_id
        ra = 98
        date = "2024-12-20T08:08:21.132394"
        
        # Al recibir el request hay dos opciones
        # 1. Aprobación automatica al recibir el STATUS = VIDEOPENDING.
        # 2. Aprobación manual descargando las imagenes y el video para que el operador apruebe la solicitud.
        
        try:
            find_video = log_oneshot.objects.get(detail=request_video)
            find_firmante = Firmante.objects.get(id=find_video.Firmante.pk)
            
            video_id = VideoIdentificacion(
                status = status,
                date = str(date),
                previous_status = previous_status,
                request = request_video,
                registration_authority = ra,
                firmante = find_firmante
            )
            video_id.save()
            
            if status == 'VIDEOPENDING':
                validar = validar_videoid(request_video)
                validar_parse = json.loads(validar)
                if validar_parse['success']:
                    time.sleep(1)
                    aprobar = aprobar_videoid(request_video)
                    aprobar_parse = json.loads(aprobar)
                    if aprobar_parse['success']:
                        enviar_correo("Solicitud de firma One-Shot", "Por favor firmar el siguiente enlace", "notificaciones@signgo.com.gt", find_firmante.correo, find_firmante.TokenAuth)
                    else:
                        None
                else:
                    None
            
            messages.success(request, 'Request guardado con éxito')
            return redirect(f'/flujo_firma/aprobacion_video_id_oneshot_temporal')
            
        except log_oneshot.DoesNotExist:
            messages.error(request, "El request recibido no existe dentro de la RA")
            return redirect(f'/flujo_firma/aprobacion_video_id_oneshot_temporal')
    else:
        find_oneshots = log_oneshot.objects.all().order_by('-id')

        contexto = {
            'oneshots': find_oneshots
        }
        
        return render(request, 'flujofirma/aprobacion_video_id_oneshot_temporal.html', contexto)



def aprobar_video(request):
    
    return render(request, 'flujofirma/aprobar_video.html')


def validarPocisiónPagina():
    return 1

def verifyPin(usuarioCliente, contraseña, pin):
    requestStatusBilling = billingSignboxSandbox.objects.get(id=1)
    
    url = "https://cryptoapi.sandbox.uanataca.com/api/verify_pin" if requestStatusBilling.status == "1" else "https://cryptoapi.uanataca.com/api/verify_pin"

    payload = json.dumps({
        "username": usuarioCliente,
        "password": contraseña,
        "pin": pin
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response_data = response.json()
    
    if response_data.get("result") is None:
        return response_data.get("error", {}).get("msg")
    return None


def translateResponse(data):
    switcher = {
        'Token not found': lambda: "Usuario Incorrecto",
        'Invalid credentials': lambda: "Contraeña Incorrecta",
        'Pin invalid': lambda: "Codigo PIN Incorrecto",
        'Token locked': lambda: "Codigo PIN Bloqueado",
        'Authentication refused': lambda: "Las credenciales ingresadas no existen"
    }
    return switcher.get(data, lambda: data)()

def signDocument(id_request, usuarioCliente, contraseña, pin, nombreDocumento, coordenadas, pagina, tokenArchivoID, getDataEstilo, url_archivo):
    try:
        getDataWebhook = webhookIP.objects.get(id=1)
    
        if getDataWebhook.protocol == "1":
            protocolo = "https"
        else:
            protocolo = "http"
        
        dataUrlOut = f'{protocolo}://{getDataWebhook.ip}/flujo_firma/result/{tokenArchivoID}'
        dataUrlBack = f'{protocolo}://{getDataWebhook.ip}/flujo_firma/services/{tokenArchivoID}'
        
        requestStatusBilling = billingSignboxProd.objects.get(id=1)
        if requestStatusBilling.status == "1":
            userBilling = requestStatusBilling.user
            passBilling = requestStatusBilling.password
            envSignbox = "prod"
        else:
            requestSandboxBilling = billingSignboxSandbox.objects.get(id=1)   
            userBilling = requestSandboxBilling.user
            passBilling = requestSandboxBilling.password
            envSignbox = "sandbox"
            
        dataAPI = signboxAPI.objects.get(id=1)
        protocolAPI = "http" if dataAPI.protocol == "0" else "https"
        newURL = protocolAPI + "://" + dataAPI.ip + "/api/sign"
        
        url = newURL
        print(url)
        dataTexto = []
        if Imagen.objects.filter(id="10000000000").exists():
            personalizacion = Imagen.objects.get(id=getDataEstilo)
            dataTexto.append("Firmado digitalmente por: $(CN)s") if personalizacion.isNombre else None
            dataTexto.append("Fecha: $(date)s") if personalizacion.isFecha else None
            dataTexto.append('"Ciudad de Guatemala, $(C)s"') if personalizacion.isUbicacion else None
            rubricaGeneral = personalizacion.Rubrica
            rubricaTamaño = personalizacion.dimensionesImagen
        else:
            dataTexto.append("Firmado digitalmente por: $(CN)s")
            dataTexto.append("Fecha: $(date)s")
            dataTexto.append('"Ciudad de Guatemala, $(C)s"')
            rubricaGeneral = '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'
            rubricaTamaño = '507,368'
        
        paragraph_format = {
            "font": ["Universal-Italic", 10],
            "align": "right",
            "data_format": {
                "timezone": "America/Guatemala",
                "strtime": "%d/%m/%Y %H:%M:%S%z"
            },
            "format": dataTexto
        }

        paragraph_format_list = [paragraph_format]
        paragraph_format_json = json.dumps(paragraph_format_list)
        
        payload = {
            'url_out': dataUrlOut,
            'urlback': dataUrlBack,
            'env': envSignbox,
            'format': 'pades',
            'username': usuarioCliente,
            'password': contraseña,
            'pin': pin,
            'level': 'BES',
            'billing_username': userBilling,
            'billing_password': passBilling,
            'reason': 'Firma Electrónica',
            'location': 'Guatemala, Guatemala',
            'img': rubricaGeneral,
            'img_name': 'uanataca.argb',
            'img_size': rubricaTamaño,
            'position': coordenadas,
            'npage': pagina,
            'paragraph_format': paragraph_format_json
        }  
        
        files = {
            'url_in': url_archivo,
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(url, data=payload, files=files)
        return json.dumps({"success": True, "data": response.text})
    except Exception as e:
        print(f'Error SignDocument: {e}')
        return json.dumps({"success": False, "error": e})
    

def saveIDFile(nombreArchivo, tokenArchivo, tokenEnvio, estutusArchivo, usuarioEnvio, IDAPI, idDocumento):
    try:
        InstanceDocumento = uploadDocument.objects.get(id=idDocumento)
        InstanceUser = Firmante.objects.get(TokenAuth=usuarioEnvio)
        InserVitacora = VitacoraFirmado(
            TokenEnvio = tokenEnvio,
            NombreArchivo = nombreArchivo,
            TokenArchivo = tokenArchivo,
            UsuarioFirmante = InstanceUser,
            EstadoFirma = estutusArchivo,
            IDArchivoAPI = IDAPI,
            documento_id = InstanceDocumento
        )
        InserVitacora.save()
        return 'OK 200'
    except Exception as e:
        print(f'Error: {e}')
        return e
    
def firmado(request, tokenFirmante):
    try:
        find_firmante = Firmante.objects.get(TokenAuth=tokenFirmante)
        getListFiles = VitacoraFirmado.objects.filter(UsuarioFirmante=find_firmante.pk)
        idError = []
        idOK = []
        detailError = []
        detailOK = []
        for idFiles in getListFiles:
            getStatusFile = VitacoraFirmado.objects.get(IDArchivoAPI=idFiles.IDArchivoAPI)
            idOK.append(idFiles.IDArchivoAPI) if getStatusFile.EstadoFirma == "Firmado" else idError.append(idFiles.IDArchivoAPI)           

        CantidadNoFirmados = (len(idError))
        CantidadFirmados = (len(idOK))
        
        if idError:
            for id in idError:
                getDetailError = VitacoraFirmado.objects.get(IDArchivoAPI=id)
                TipoError = TranslateError(getDetailError.EstadoFirma)
                detailError.append([getDetailError.NombreArchivo, TipoError])
            
            for id in idOK:
                getDetailSuccess = VitacoraFirmado.objects.get(IDArchivoAPI=id)
                detailOK.append([getDetailSuccess.NombreArchivo, getDetailSuccess.EstadoFirma, getDetailSuccess.url_archivo])
        else:
            for id in idOK:
                getDetailSuccess = VitacoraFirmado.objects.get(IDArchivoAPI=id)
                detailOK.append([getDetailSuccess.NombreArchivo, getDetailSuccess.EstadoFirma, getDetailSuccess.url_archivo])
        
        type_device = is_mobile(request)
        
        contexto = {
            'CantidadNoFirmados': CantidadNoFirmados,
            'CantidadFirmados': CantidadFirmados,
            'getDetailError': detailError,
            'getDetailSuccess': detailOK,
            'is_mobile': type_device
        }
        return render(request, 'flujofirma/validar_firmado.html', contexto)
    except Exception as e:
        print(f'Error: {e}')
        return render(request, 'flujofirma/validar_firmado.html')
    
def TranslateError(data):
    switcher = {
        'NoMatch': "Archivo Corrupto o Dañado",
        'ProcessTerminated': "Error de comunicación con servidor de archivos"
    }
    
    for key in switcher:
        if key in data:
            return switcher[key]
    
    return data

@csrf_exempt
def videoid(request):
    if request.method == 'POST':
        request_parse = json.loads(request.body)
        status = request_parse.get('status', None)
        date = request_parse.get('date', None)
        previous_status = request_parse.get('previous_status', None)
        request_video = request_parse.get('request', None)
        ra = request_parse.get('registration_authority', None)
        print(f'{request_video}')
        
        # Al recibir el request hay dos opciones
        # 1. Aprobación automatica al recibir el STATUS = VIDEOPENDING.
        # 2. Aprobación manual descargando las imagenes y el video para que el operador apruebe la solicitud.
        
        try:
            find_video = log_oneshot.objects.get(detail=request_video)
            find_firmante = Firmante.objects.get(id=find_video.Firmante.pk)
            
            video_id = VideoIdentificacion(
                status = status,
                date = str(date),
                previous_status = previous_status,
                request = request_video,
                registration_authority = ra,
                firmante = find_firmante
            )
            video_id.save()
            
            if status == 'VIDEOREVIEW':
                validar = validar_videoid(request_video)
                validar_parse = json.loads(validar)
                if validar_parse['success']:
                    time.sleep(1)
                    aprobar = aprobar_videoid(request_video)
                    aprobar_parse = json.loads(aprobar)
                    if aprobar_parse['success']:
                        enviar_correo("Solicitud de firma One-Shot", "Por favor firmar el siguiente enlace", "notificaciones@signgo.com.gt", find_firmante.correo, find_firmante.TokenAuth)
                    else:
                        None
                else:
                    None
                
            
            return JsonResponse({"success": True, "data": "Request guardado con éxito"})
            
        except log_oneshot.DoesNotExist:
            print("El request recibido no existe dentro de la RA")
            return JsonResponse({"success": True, "data": "request not found"}, status=200)
        
        # return JsonResponse({"success": True, "data": "Datos Procesados"}, status=200)
    return server_error(request)

def validar_videoid(request_video):

    protocolo, ip = validar_API_oneshot()
    
    url = f'{protocolo}://{ip}/api/v1/videoid/{request_video}/validate'
    
    find_token = token_oneshot.objects.filter().first()


    payload = json.dumps({
        "token": find_token.token,
        "username": "1108124",
        "password": "29yqdGGw",
        "pin": "belorado74",
        "rao": "98"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response_parse = json.loads(response.text)
    print(response.text)
    if response_parse['status'] == "200 OK":
        return json.dumps({"success": True, "data": response_parse['details']})
    else:
        return json.dumps({"success": False, "error": response_parse['details']})


def aprobar_videoid(request_video):
    
    protocolo, ip = validar_API_oneshot()
    
    url = f'{protocolo}://{ip}/api/v1/request/{request_video}/approve'
    
    find_token = token_oneshot.objects.filter().first()

    payload = json.dumps({
        "token": find_token.token,
        "username": "1108124",
        "password": "29yqdGGw",
        "pin": "belorado74",
        "rao": "98"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response_parse = json.loads(response.text)
    print(response.text)
    if response_parse['status'] == "200 OK":
        return json.dumps({"success": True, "data": response_parse['details']})
    else:
        return json.dumps({"success": False, "error": response_parse['details']})
    
def get_token(request):
    if request.method == 'POST':
        try:
            token_request = json.loads(request.body)
            firmante_request = token_request.get('request', None)

            protocolo, ip = validar_API_oneshot()
            
            url = f'{protocolo}://{ip}/api/v1/otp/{firmante_request}'

            payload = json.dumps({
                "delivery_method": "whatsapp"
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            print(response.text)
            response_parse = json.loads(response.text)
            if response_parse['status'] == '200 OK':
                return JsonResponse({"success": True, "data": "token enviado con éxito"}, status=200)
            else: 
                return JsonResponse({"success": False, "error": "Error al generar el token"})
            # print("recibido")
            # return JsonResponse({"success": True, "data": "token enviado con éxito"}, status=200)
        except Exception:
            return JsonResponse({"success": False, "error": "Error al enviar el token"})
    else:
        return JsonResponse({"success": False, "error": "Esta página no acepta solicitudes GET"})
    
def firmar_documento_oneshot(request, tokenFirmante):
    new_url = f'/flujo_firma/validar_documento/{tokenFirmante}'
    try:
        token_otp = request.POST.get('inputToken')
        find_firmante = Firmante.objects.get(TokenAuth=tokenFirmante)
        find_documents = detalleFirma.objects.filter(firmante=find_firmante.pk)
        find_request = log_oneshot.objects.get(Firmante=find_firmante.pk)
        find_carpeta = documentos.objects.get(tokenEnvio=find_firmante.envio.TokenAuth)
        
        # PASO 1 = GUARDAR ESTADO FIRMANDO
        print(f'Archivos de firmante: {find_documents.count()}')
        
        
        # PASO 2 = CARGAR LOS DOCUMENTOS AL API
        for documento in find_documents:
            response_document = upload_document(documento.documento.nombre_documento, find_carpeta.nameCarpeta, documento.documento.url_documento, find_request.detail)
            response_parse_document = json.loads(response_document)
            if response_parse_document['success']:
                documento.request_upload_document = response_parse_document['data']
                documento.save()
            else:
                messages.error(request, f"Error al cargar documentos: {response_parse_document['error']}")
                return redirect(f'/flujo_firma/validar_documento/{tokenFirmante}')
        
        # PASO 3 = FIRMAR LOS DOCUMENTOS
        print("Paso 3")
        response_sign = sign_documents(tokenFirmante, token_otp, find_request.detail)
        response_sign_parse = json.loads(response_sign)
        
        if response_sign_parse['success']:
            find_firmante.is_firmado = True
            find_firmante.fecha_firmado = timezone.now()
            find_firmante.save()
        else:
            print("error al confirmar si se había firmado el documento")
            raise Exception("Error al guardar el status del documento")
        
        # PASO 4 = RECUPERAR LOS DOCUMENTOS
        print("paso 4")
        response_retrieve_documents = retrieve_documents(tokenFirmante, find_request.detail, find_carpeta.nameCarpeta, )
        response_retrieve_documents_parse = json.loads(response_retrieve_documents)
        
        if response_retrieve_documents_parse['success']:
            
            if find_firmante.envio.flujo_por_orden == True:
                result = envio_ordenado(find_firmante.envio.TokenAuth)
            else:
                result = envio_masivo(find_firmante.envio.TokenAuth)
            
            return redirect(f'/flujo_firma/confirmacion_firmado/{tokenFirmante}') 
        else:
            raise Exception("Error al guardar el archivo firmado")
        
    except Exception as e:
        messages.error(request, f"Error al cargar los documentos al API: {e}")
        return redirect(f'/flujo_firma/validar_documento/{tokenFirmante}')
    

def upload_document(nombre_documento, carpeta_documento, url_documento, request_oneshot):
    try:
        
        protocolo, ip = validar_API_oneshot()

        url = f'{protocolo}://{ip}/api/v1/document/{request_oneshot}'  
        
        file_in_memory = descargar_archivo(url_documento)
        
        if file_in_memory is None:
            return json.dumps({"success": False, "error": "Error al descargar el archivo."})
        
        
        payload={}
        files = []
        
        files.append(('file', (nombre_documento, file_in_memory, 'application/pdf')))
        response = requests.request("POST", url, data=payload, files=files)
        response_parse = json.loads(response.text)
        
        return json.dumps({"success": True, "data": response_parse['details']})
    except Exception as e:
        return json.dumps({"success": False, "error": f"Error en la solicitud: {e}"})

def descargar_archivo(url_documento):
    try:
        response = requests.get(url_documento)
        if response.status_code == 200:
            file_in_memory = BytesIO(response.content)
            return file_in_memory
        else:
            return None
    except Exception as e:
        print(f"Error al descargar el archivo: {e}")
        return None
    
def sign_documents(tokenFirmante, token_OTP, request_oneshot):
    
    protocolo, ip = validar_API_oneshot()
    
    url = f"{protocolo}://{ip}/api/v1/sign/{request_oneshot}"
    
    # Obtener el firmante y los documentos asociados
    find_firmante = Firmante.objects.get(TokenAuth=tokenFirmante)
    find_documents = detalleFirma.objects.filter(firmante=find_firmante.pk)
    
    options = {}
    for documento in find_documents:
    
        options[documento.request_upload_document] = {
            "position": f'{documento.p_x1}, {documento.p_y1}, {documento.p_x2}, {documento.p_y2}',
            "page": documento.pagina
        }
    
    payload = json.dumps({
        "secret": token_OTP,
        "disable_ltv": True,
        "use_signature_text": True,
        "options": options
    })
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response_parse = json.loads(response.text)
        print(f"respuesta del api al firmar: {response.text}")
        if response_parse['status'] == '200 OK':
            return json.dumps({"success": True, "data": "Signed"})  
        else:
            raise Exception(response_parse['details'])
    except Exception as e:
        print(e)
        return json.dumps({"success": False, "error": str(e)})
    
def retrieve_documents(tokenFirmante, request_oneshot, nombre_carpeta):
    try:
        find_firmante = Firmante.objects.get(TokenAuth=tokenFirmante)
        find_documents = detalleFirma.objects.filter(firmante=find_firmante.pk)
        
        protocolo, ip = validar_API_oneshot()
        
        for documento in find_documents:

            url = f"{protocolo}://{ip}/api/v1/document/{request_oneshot}/signed/{documento.request_upload_document}"

            payload = ""
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            
            if "application/json" in response.headers.get("Content-Type", ""):
                response_parse = json.loads(response.text)
                raise Exception(response_parse['details'])
            else:
                nombre_archivos = []
                
                nombreCarpeta = nombre_carpeta
                base_path = 'media/flujofirma/FilesNoFirmados/'
                urls = []

                # for pdf_file in pdf_files:
                nueva_archivo = ArchivosPDF()
                nombre_inicial = documento.documento.nombre_documento
                nombre_archivos.append(nombre_inicial)
                nueva_archivo.set_upload_paths(base_path, nombreCarpeta)
                nueva_archivo.archivo.save(nombre_inicial, ContentFile(response.content))
                nueva_archivo.save()
                presigned_url = nueva_archivo.get_presigned_url()
                urls.append(presigned_url) 
                
                update_url_document = uploadDocument.objects.get(url_documento=documento.documento.url_documento)  
                update_url_document.url_documento = presigned_url
                update_url_document.save()
 
                
        return json.dumps({"success": True, "data": "200 OK"}) 
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})
    
def confirmacion_firmado(request, tokenFirmante):
    find_firmante = Firmante.objects.get(TokenAuth=tokenFirmante)
    find_documents = detalleFirma.objects.filter(firmante=find_firmante.pk)
    
    contexto = {
        'archivos_firmados': find_documents
    }
    
    return render(request, 'flujofirma/confirmacion_firmado.html', contexto)

def historial_flujos(request):
    
    get_envios = Envio.objects.all().order_by('-id')
    
    contexto = {
        'envios': get_envios
    }
    
    return render(request, 'flujofirma/historial_flujos.html', contexto)




def validación_licencia(usuarioID):
    try:
        validate_perfil = PerfilSistema.objects.get(usuario=usuarioID)
        validate_user = UsuarioSistema.objects.get(UsuarioGeneral=usuarioID)
        if validate_perfil.empresa == None:
            validate_licencia = LicenciasSistema.objects.filter(usuario=validate_user.id, tipo='FF_Oneshot').order_by('-id').last()
            
            if validate_licencia.licencia_vencida():
                return json.dumps({"success": False, "error": "Licencia Expirada"})
            
            if int(validate_licencia.porcentaje) == 100:
                return json.dumps({"success": False, "error": "Creditos Agotados"})
            else: 
                return json.dumps({"success": True, "data": "OK", "tipo_licencia": validate_licencia.env, "id_licencia": validate_licencia.id})
        
        return json.dumps({"success": True, "data": "OK", "tipo_licencia": validate_licencia.env, "id_licencia": validate_licencia.id})
    except Exception as e:
        return json.dumps({"success": False, "error": f"No se ha podido encontrar su licencia"})


def validar_API_oneshot():
    
    dataOneshot = oneshotAPI.objects.get(id=1)
    protocol = "http" if dataOneshot.protocol == "0" else "https"
    ip = dataOneshot.ip    
    
    return protocol, ip
    
    
    

