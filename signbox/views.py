from django.shortcuts import render, redirect
import os
from django.conf import settings
from .models import documentos
import secrets
from django.http import HttpResponse
import requests
from django.contrib import messages
import json
import re
from .models import billingSignboxProd, billingSignboxSandbox, signboxAPI, VitacoraFirmado, Imagen, ArchivosPDF, credencialesCert, documentos_eliminados, detalleFirma
import random
import time
from django.contrib.auth.decorators import login_required
from webhook.models import webhookIP
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.utils import timezone
import io
from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from datetime import timedelta
import base64 
from django.urls import reverse
from PIL import Image
from django.core.files.storage import default_storage
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.utils.timezone import now
from .models import ArchivosPDF
from django.views.decorators.csrf import csrf_exempt
from app.models import LicenciasSistema, UsuarioSistema, PerfilSistema
from urllib.parse import unquote, urlparse
from django.core.files.uploadedfile import InMemoryUploadedFile


def validatePermissions(user):
    return user.groups.filter(name='SignboxAuth').exists()

def helloworld(request):
    archivo_pdf = os.path.join(settings.MEDIA_URL, 'pagoPlanilla/boletasSign/338064101078580/275/boleta_de_pago.pdf')
    contexto = {
        'url_to_pdf': archivo_pdf
    }
    return render(request, 'signbox/helloworld.html', contexto)

@login_required
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
def uploadFiles(request):
    if request.method == "POST":
        nombre_archivos = []
        pdf_files = request.FILES.getlist('pdf_files')
        
        nombreCarpeta = random.randint(100000000000000, 999999999999999) 
        base_path = 'media/signbox/FilesNoFirmados/'
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
                        
        tokenDocumentos = secrets.token_urlsafe(25)
        requestDocumentos = documentos(
            status="NoFirmado",
            secret=tokenDocumentos,
            nameArchivos=nombre_archivos,
            url_archivos=urls,
            nameCarpeta=str(nombreCarpeta)
        )
        requestDocumentos.save()    
        newURL = "/firma_agil/verifyDocs/" + tokenDocumentos
        return redirect(newURL)
    
    
    validate = validación_licencia(request.user.id)
    validate_parse = json.loads(validate)
    reason_error = None

    if validate_parse['success']:
        estado = "activa"
    else:
        if validate_parse['error'] == 'Creditos Agotados':
            messages.error(request, validate_parse['error'])
            estado = "creditos"
        elif validate_parse['error'] == 'No se ha podido encontrar su licencia':
            messages.error(request, validate_parse['error'])
            estado = "404"
        else:
            messages.error(request, validate_parse['error'])
            estado = "expirada"
    
    contexto = {
        'licencia': estado        
    }
    
    if is_mobile(request):
        # return render(request, 'signbox/asignar_firma.html', contexto)    
        return render(request, "signbox/uploadFiles_movl_device.html", contexto)
    else:
        return render(request, "signbox/uploadFiles.html", contexto)
    
    

@login_required
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
def verifyDocs(request, request_id):
    
    new_url = "/firma_agil/verifyDocs/" + request_id
    
    dataDocuments = documentos.objects.get(secret=request_id)
    nameCarpeta = dataDocuments.nameCarpeta
    listDocuments = dataDocuments.nameArchivos
    list_urls = dataDocuments.url_archivos
    viewDocuments = []
    for nombre, url in zip(listDocuments, list_urls):
        viewDocuments.append([nombre, '310KB', url])
    
    num_archivos = len(viewDocuments)
    
    # Validar si las credenciales estan guardadas
    try:
        isCkecked = credencialesCert.objects.get(user_system=request.user.id)
        user_cert = isCkecked.usuario_cert
        user_pass = isCkecked.pass_cert 
        isCkecked = True
    except ObjectDoesNotExist:
        isCkecked = False
        user_cert = ''
        user_pass = ''
    except Exception as e:
        print(f'Error al buscar las credenciales: {e}')
    
    if request.method == "POST":
        try:
            usuarioCliente = request.POST['inputUsuario']
            contraseña = request.POST['inputContraseña']
            pin = request.POST['inputPin']
            numeroPagina = request.POST['selectedPage']
            posicionPagina = request.POST['selectedPosition']
            rememberCredentials = request.POST.get('rememberCredentials', 'off') == 'on'
            
            print(f'pagina: {numeroPagina}, posicion: {posicionPagina}')
            
            if numeroPagina:
                pagina = int(numeroPagina) - 1
                pagina = str(pagina)
            else: 
                pagina = "0"
                
            if posicionPagina:
                coordenadas = validarPocisiónPagina(posicionPagina)
            else:
                coordenadas = '300,100,550,150'

            
            validatePin = verifyPin(usuarioCliente, contraseña, pin)
            idsAPI = []
            idError = []
            idOK = []
            if validatePin == None:
                
                if Imagen.objects.filter(UsuarioSistema=request.user.id, is_predeterminado=True).exists():
                    getDataEstilo = Imagen.objects.get(UsuarioSistema=request.user.id, is_predeterminado=True)
                    getIdEstilo = getDataEstilo.id
                else: 
                    getIdEstilo = None
            
                for nombreDocumento, url_file in zip(listDocuments, list_urls):
                    if rememberCredentials:
                        saveCredentials(request.user.id, usuarioCliente, contraseña)
                    else:
                        deleteCredentials(request.user.id)
                    tokenArchivo = secrets.token_urlsafe(50)
                    idFirma = signDocument(request_id, usuarioCliente, contraseña, pin, nombreDocumento, nameCarpeta, coordenadas, pagina, tokenArchivo, getIdEstilo, url_file)
                    saveIDFile(nombreDocumento, tokenArchivo, request_id, "Pendiente", request.user.id, idFirma)
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
                    url_sign = "/firma_agil/signDocs/" + request_id
                    return redirect(url_sign)
                else:
                    messages.error(request, 'Error al Firmar. Por favor intentelo mas tarde.')
                    return redirect(new_url)
        except Exception as e:
            return print(f'Error: {e}')
        
        reasonError = translateResponse(validatePin)
        messages.error(request, reasonError)
        return redirect(new_url)
    
    contexto = {
        'documentos': viewDocuments,
        'carpeta': nameCarpeta,
        'usuario_cert': user_cert,
        'pass_cert': user_pass,
        'isChecked': isCkecked
    } 

    
    if num_archivos == 1:    
        return render(request, "signbox/sign.html", contexto)
    else:
        return render(request, "signbox/sign.html", contexto)

def validarPocisiónPagina(posicionPagina):
    switcher = {
        '1': lambda: "80,620,250,670",
        '2': lambda: "215,620,385,670",
        '3': lambda: "380,620,550,670",
        '4': lambda: "80,460,250,510",
        '5': lambda: "215,460,385,510",
        '6': lambda: "380,460,550,510",
        '7': lambda: "80,300,250,350",
        '8': lambda: "215,300,385,350",
        '9': lambda: "380,300,550,350",
        '10': lambda: "80,140,250,190",
        '11': lambda: "215,140,385,190",
        '12': lambda: "380,140,550,190",
    }
    return switcher.get(posicionPagina, lambda: posicionPagina)()

def verifyPin(usuarioCliente, contraseña, pin, usuario_licencia):
    
    validate_licencia = validación_licencia(usuario_licencia)
    validate_licencia_parse = json.loads(validate_licencia)
    
    if validate_licencia_parse['tipo_licencia'] == 'sandbox':
        url = "https://cryptoapi.sandbox.uanataca.com/api/verify_pin"
    else:
        url = "https://cryptoapi.uanataca.com/api/verify_pin"
    
    

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

def tokenInfo():
    return "hola"

def translateResponse(data):
    switcher = {
        'Token not found': lambda: "Usuario Incorrecto",
        'Invalid credentials': lambda: "Contraeña Incorrecta",
        'Pin invalid': lambda: "Codigo PIN Incorrecto",
        'Token locked': lambda: "Codigo PIN Bloqueado"
    }
    return switcher.get(data, lambda: data)()

def signDocument(id_request, usuarioCliente, contraseña, pin, nombreDocumento, nameCarpeta, coordenadas, pagina, tokenArchivoID, getDataEstilo, url_archivo, usuario_licencia):
    try:
        
        getDataWebhook = webhookIP.objects.get(id=1)

        if getDataWebhook.protocol == "1":
            protocolo = "https"
        else:
            protocolo = "http"
        
        
        dataUrlOut = f'{protocolo}://{getDataWebhook.ip}/result/{tokenArchivoID}'
        dataUrlBack = f'{protocolo}://{getDataWebhook.ip}/services/{tokenArchivoID}'
        
        # OBTENER LICENCIA Y CREDENCIALES DE LICENCIA
        
        validate_licencia = validación_licencia(usuario_licencia)
        validate_licencia_parse = json.loads(validate_licencia)
        
        if validate_licencia_parse['tipo_licencia'] == 'sandbox':
            envSignbox = "sandbox"
        else:
            envSignbox = "prod"
            
        validate_identifier = idetifier_signcloud(usuarioCliente, contraseña, envSignbox)
        validate_identifier_parse = json.loads(validate_identifier)
        identifier = 'DS0'
        
        if validate_identifier_parse['success']:
            identifier = validate_identifier_parse['data']  

        licencia_usuario = LicenciasSistema.objects.get(id=validate_licencia_parse['id_licencia'])
            
        userBilling = licencia_usuario.usuario_billing
        passBilling = licencia_usuario.contrasena_billing
              
            
        dataAPI = signboxAPI.objects.get(id=1)
        protocolAPI = "http" if dataAPI.protocol == "0" else "https"
        newURL = protocolAPI + "://" + dataAPI.ip + "/api/sign"
        
        print(newURL)
        
        url = newURL
        
        dataTexto = []
        if Imagen.objects.filter(id=getDataEstilo).exists():
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
            rubricaTamaño = '720, 404'
        
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
            'identifier': identifier,
            'paragraph_format': paragraph_format_json
        }  
        
        urlArchivos = './media/signbox/FilesNoFirmados/' + nameCarpeta + "/"
        ruta_archivo = os.path.join(urlArchivos, nombreDocumento)
        # url_in
        # files = {
        #     'file_in': ('PruebaFirma.pdf', open(ruta_archivo, 'rb')),
        # }
        
        files = {
            'url_in': url_archivo,
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(url, data=payload, files=files)
        
        print(f'Respuesta de endpoint sign: {response.text}')
        return response.text
    except Exception as e:
        print(f'Error SignDocument: {e}')
        return redirect(f'/verifyDocs/1')
    

def saveIDFile(nombreArchivo, tokenArchivo, tokenEnvio, estutusArchivo, usuarioEnvio, IDAPI):
    try:
        InstanceUser = User.objects.get(id=usuarioEnvio)
        InserVitacora = VitacoraFirmado(
            TokenEnvio = tokenEnvio,
            NombreArchivo = nombreArchivo,
            TokenArchivo = tokenArchivo,
            UsuarioFirmante = InstanceUser,
            EstadoFirma = estutusArchivo,
            IDArchivoAPI = IDAPI
        )
        InserVitacora.save()
        return 'OK 200'
    except Exception as e:
        print(f'Error: {e}')
        return e


def idetifier_signcloud(usuario, contraseña, env):
    try:
        if env == 'sandbox':
            url = "https://cryptoapi.sandbox.uanataca.com/api/get_objects"
        else:
            url = "https://cryptoapi.uanataca.com/api/get_objects"

        payload = json.dumps({
            "username": usuario,
            "password": contraseña,
            "type": None,
            "identifier": None
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        response_parse = json.loads(response.text)
        
        ckaid = response_parse['result'][0]['ckaid']
        
        return json.dumps({'success': True, 'data': ckaid})
    except Exception as e:
        return json.dumps({'success': False, 'error': e})

@login_required
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
def verifySignDocs(request, request_id):
    try:
        getListFiles = VitacoraFirmado.objects.filter(TokenEnvio=request_id)
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
        
        if CantidadFirmados > 0:
            
            validate_perfil = PerfilSistema.objects.get(usuario=request.user.id)
            if validate_perfil.empresa == None:
                validate_user = UsuarioSistema.objects.get(UsuarioGeneral=validate_perfil.usuario.pk)
                licencia_usuario = LicenciasSistema.objects.filter(usuario=validate_user.pk, tipo='Firma Agil').last()
                licencia_usuario.consumo = licencia_usuario.consumo + int(CantidadFirmados)
            else:            
                licencia_usuario = LicenciasSistema.objects.filter(empresa=validate_perfil.empresa.id, tipo='Firma Agil').order_by('-id').last()
                licencia_usuario.consumo = licencia_usuario.consumo + int(CantidadFirmados)
            
            
            licencia_usuario.save()
            
            
        contexto = {
            'CantidadNoFirmados': CantidadNoFirmados,
            'CantidadFirmados': CantidadFirmados,
            'getDetailError': detailError,
            'getDetailSuccess': detailOK
        }
        return render(request, "signbox/firmados.html", contexto)
    except Exception as e:
        print(f'Error: {e}')
        messages.error(request, f'Error al obtener documentos: {e}')
        return render(request, "signbox/firmados.html")
    
    
def TranslateError(data):
    switcher = {
        'NoMatch': "Archivo Corrupto o Dañado",
        'ProcessTerminated': "Error de comunicación con servidor de archivos"
    }
    
    for key in switcher:
        if key in data:
            return switcher[key]
    
    return data

@login_required
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
def historial(request):
    
    if request.method == 'POST':
        try:
            NombreArchivo = request.POST.get('nombreEmpresa', '')
            fecha_desde = request.POST.get('fechaRegistroDesde', '')
            fecha_hasta = request.POST.get('fechaRegistroHasta', '')
            
            GetProcesosFirmado = VitacoraFirmado.objects.filter(EstadoFirma="Firmado", UsuarioFirmante=request.user.id).order_by('-id')
            
            if NombreArchivo:
                GetProcesosFirmado = GetProcesosFirmado.filter(NombreArchivo__icontains=NombreArchivo)
                
            if fecha_desde:
                GetProcesosFirmado = GetProcesosFirmado.filter(FechaFirmado__gte=fecha_desde)
                
            if fecha_hasta:
                GetProcesosFirmado = GetProcesosFirmado.filter(FechaFirmado__lte=fecha_hasta)
            
            contexto = {
                'ProcesosFirmado': GetProcesosFirmado,
                'FiltroNombre': NombreArchivo,
                'FiltroDesde': fecha_desde,
                'FiltroHasta': fecha_hasta,
            }
            return render(request, 'signbox/historial.html', contexto)
        except Exception as e:
            print(f'Error: {e}')
        return render(request, 'signbox/historial.html')
    
    try:        
        GetProcesosFirmado = VitacoraFirmado.objects.filter(EstadoFirma="Firmado", UsuarioFirmante=request.user.id).order_by('-id')
        GetDocumentosDelete = documentos_eliminados.objects.filter(usuario_firmante=request.user.id)
        contexto = {
            'ProcesosFirmado': GetProcesosFirmado,
            'DocumentosEliminados': GetDocumentosDelete
        }
        return render(request, 'signbox/historial.html', contexto) 
    except Exception as e:
        print(f'Error: {e}')
        return render(request, 'signbox/historial.html')
    
def enviar_correo(request):
    if request.method == 'POST':
        try:
            time.sleep(3)
            request_parse = json.loads(request.body)
            print(f"request a enviar: {str(request_parse.get('request_id_documento', None))}")
            print(f"contactos a enviar: {str(request_parse.get('contactos', None))}")

            return JsonResponse({"success": True, "data": "correo enviado con exito"}, status=200)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    else:
        return JsonResponse({"success": False, "error": "Esta página no acepta solicitudes"})
    
def eliminar_documento(request, TokenAuth):
    if request.method == 'POST':
        try:
            find_vitacora = VitacoraFirmado.objects.get(id=TokenAuth)
            usuario_delete = User.objects.get(id=request.user.id)
            
            save_delete = documentos_eliminados(
                nombre_documento = find_vitacora.NombreArchivo,
                usuario_firmante = usuario_delete
            )
            save_delete.save()    
            find_vitacora.delete()
            messages.success(request, "Documento Eliminado con Éxito")
        except Exception as e:
            messages.error(request, "Ocurrió un error al eliminar el documento")
    else:
        return JsonResponse("Esta URL no acepta peticiones")

    return redirect('/firma_agil/historial')


    
def generar_reporte(request):
    NombreArchivo = request.POST.get('nombreEmpresa', '')
    fecha_desde = request.POST.get('fechaRegistroDesde', '')
    fecha_hasta = request.POST.get('fechaRegistroHasta', '')
    
    GetProcesosFirmado = VitacoraFirmado.objects.filter(EstadoFirma="Firmado", UsuarioFirmante=request.user.id).order_by('-id')
    
    now_utc = timezone.now()
    now_utc_minus_6 = now_utc
    
    if NombreArchivo:
        GetProcesosFirmado = GetProcesosFirmado.filter(NombreArchivo__icontains=NombreArchivo)
                
    if fecha_desde:
        GetProcesosFirmado = GetProcesosFirmado.filter(FechaFirmado__gte=fecha_desde)
                
    if fecha_hasta:
        GetProcesosFirmado = GetProcesosFirmado.filter(FechaFirmado__lte=fecha_hasta)

    contexto = {
        'Envios': GetProcesosFirmado,
        'current_date': now_utc_minus_6
    }
    archivo = 'reporteFirmado.html'
        
    getPDF = make_pdf(archivo, contexto)       
    response = getPDF
    return response

def make_pdf(archivo, contexto):

    html_renderizado = render_to_string(f'ReportesFirmado/{archivo}', contexto)
    
    pdf_buffer = io.BytesIO()
    
    pisa_status = pisa.CreatePDF(html_renderizado, dest=pdf_buffer)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=400)

    pdf_buffer.seek(0)  # Asegurarse de estar al inicio del archivo
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte.pdf"'

    return response

@login_required
def personalizar(request):
    
    validar_link_imagen(request.user.id)
    
    getEstiloFirma = Imagen.objects.filter(UsuarioSistema=request.user.id).order_by('-id')
    
    contexto = {
        'estilos': getEstiloFirma
    }
    
    return render(request, 'signbox/personalizar.html', contexto)

def eliminar_estilo(request, TokenAuth):
    get_estilo = Imagen.objects.get(id=TokenAuth)
    get_estilo.delete()
    messages.success(request, 'Estilo eliminado con éxito')
    return redirect(reverse('personalizar')) 

def guardar_imagen(request):
    if request.method == 'POST':
        
            archivos = request.FILES['firmaImagen']  # Obtener imagen del formulario
            archivo_redimensionado, imagen_base_64 = redimensionar_imagen(archivos)
            archivos = archivo_redimensionado
            
            imagen_base64 = imagen_base_64
            siNombre = request.POST.get('opcionNombre')
            siFecha = request.POST.get('opcionFecha')
            siUbicacion = request.POST.get('opcionUbicacion')
            
            valorNombre = True if siNombre else False
            valorFecha = True if siFecha else False
            valorUbicacion = True if siUbicacion else False
            
            
            
            with Image.open(archivos) as img:
                ancho, alto = img.size
                
            usuario_id = request.user.id
            usuarioFirma = User.objects.get(id=request.user.id)
            
            base_path = 'media/signbox/Rubrica/'
            folder_name = f'user_{usuario_id}'
            nueva_imagen = Imagen()
            nueva_imagen.set_upload_paths(base_path, folder_name)
            nueva_imagen.imagen = archivos
            nueva_imagen.UsuarioSistema = usuarioFirma
            nueva_imagen.Rubrica = imagen_base64
            nueva_imagen.isNombre = valorNombre
            nueva_imagen.isFecha = valorFecha
            nueva_imagen.dimensionesImagen= f'{ancho}, {alto}'
            nueva_imagen.isUbicacion = valorUbicacion
            nueva_imagen.save()
            presigned_url = nueva_imagen.get_presigned_url()
            nueva_imagen.presigned_url = presigned_url
            nueva_imagen.save()
            
            messages.success(request, "Estilo guardado con éxito.")
            return redirect(reverse('personalizar'))
        
def redimensionar_imagen(imagen, ancho_base=300):
    with Image.open(imagen) as img:
        # Tomar el ancho original de la imagen
        ancho_original = img.width
        
        # Calcular la altura basada en la proporción 3:4
        altura_calculada = int(ancho_original * 3 / 4)
        
        # Redimensionar la imagen manteniendo la proporción 3:4
        img = img.resize((ancho_original, altura_calculada), Image.Resampling.LANCZOS)
        
        # Guardar la imagen ajustada en memoria
        img_io = BytesIO()
        img_format = img.format if img.format else 'JPEG'  # Usar el formato original o JPEG
        img.save(img_io, format=img_format)
        
        # Crear un nuevo archivo que pueda ser guardado
        nueva_imagen = InMemoryUploadedFile(
            img_io,  # Contenido de la imagen
            None,  # Nombre del campo
            imagen.name,  # Nombre del archivo original
            f'image/{img_format.lower()}',  # Tipo MIME
            img_io.tell(),  # Tamaño del archivo
            None  # Codificación
        )
        
        img_io.seek(0)  # Volver al inicio del buffer
        imagen_base64 = base64.b64encode(img_io.read()).decode('utf-8')
        
        return nueva_imagen, imagen_base64

    
def select_imagen(request, estilo_id):
    if request.method == 'POST': 
        try:
            Imagen.objects.filter(UsuarioSistema=request.user.id).update(is_predeterminado=False)
            insertEstilo = Imagen.objects.get(id=estilo_id)
            insertEstilo.is_predeterminado = True
            insertEstilo.save()
            messages.success(request, "Estilo predeterminado guardado con éxito.")
            return redirect(reverse('personalizar'))
        except Exception as e:
            print(f'Error: {e}')
            messages.warning(request, "Error al guardar el estilo predeterminado, favor intentelo más tarde.")
            return redirect(reverse('personalizar'))
    else:
        return HttpResponse('Metodo no permitido')
    
def saveCredentials(usuario_system, usuario_crt, pass_crt):
    try:
        get_user = credencialesCert.objects.get(user_system=usuario_system)
        get_user.usuario_cert = usuario_crt
        get_user.pass_cert = pass_crt
        get_user.save()
        return '200 OK'
    except ObjectDoesNotExist:
        user_id = User.objects.get(id=usuario_system)
        insert_credentials = credencialesCert(
            user_system = user_id,
            usuario_cert = usuario_crt,
            pass_cert = pass_crt
        )
        insert_credentials.save()
    except Exception as e:
        return print(f'Error al guardar las credenciales: {e}')
  
    
def deleteCredentials(usuario_system):
    try:
        get_credentials = credencialesCert.objects.get(user_system=usuario_system)
        get_credentials.delete()
        return '200 OK'
    except ObjectDoesNotExist:
        return '200 OK'
    except Exception as e:
        return print(f'Error al eliminar las credenciales: {e}')
    
def watchDocument(request, id_request):
    try:
        get_request = VitacoraFirmado.objects.get(TokenArchivo=id_request)
        
        validar_link = validar_Link_Archivo(id_request)
        if not validar_link == 'OK':
            get_request.url_archivo = validar_link
            get_request.save()
        
        get_request = VitacoraFirmado.objects.get(TokenArchivo=id_request)
        contexto = {
            'archivos': get_request
        }
    except Exception as e:
        print(f'Error al buscar el archivo: {e}')
    return render(request, 'signbox/watchDocument.html', contexto)


def validar_Link_Archivo(token): 
    try:
        archivo = ArchivosPDF.objects.get(token_archivo=token)

        if archivo.url_firmada_expiracion and archivo.url_firmada_expiracion > now():
            return 'OK'
            
        nueva_url = archivo.get_presigned_url()
        return nueva_url
    
    except ArchivosPDF.DoesNotExist:
        return print(f'Archivo no encontrado')
    
def validar_link_imagen(usuario): 
    try:
        imagenes_usuario = Imagen.objects.filter(UsuarioSistema=usuario)

        for archivo in imagenes_usuario:
            if archivo.url_firmada_expiracion and archivo.url_firmada_expiracion > now():
                return 'OK'
                
            nueva_url = archivo.get_presigned_url()
            archivo.presigned_url = nueva_url
            archivo.save()
        
        return 'Update'
    except Imagen.DoesNotExist:
        return print(f'Archivo no encontrado')
    
def is_mobile(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    
    # Expresión regular para detectar dispositivos móviles
    mobile_regex = re.compile(r"android|iphone|ipod|blackberry|windows phone", re.I)
    
    if mobile_regex.search(user_agent):
        return True
    
    return False
    
@csrf_exempt
@login_required
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
def asignar_firma(request, tokenEnvio):

    new_url = "/firma_agil/verifyDocs/" + tokenEnvio
    
    if request.method == "POST":
        try:
            usuarioCliente = request.POST['userInput']
            contraseña = request.POST['userpsw']
            pin = request.POST['userpin']
            rememberCredentials = request.POST.get('save_credentials', 'off') == 'on'
            validatePin = verifyPin(usuarioCliente, contraseña, pin, request.user.id)
            
            firma_lote = request.POST.get('firma_estatica', 'off') == 'on'
            print(firma_lote)
            dataDocuments = documentos.objects.get(secret=tokenEnvio)
            nameCarpeta = dataDocuments.nameCarpeta
            
            idsAPI = []
            idError = []
            idOK = []
            
            if validatePin == None:
                
                if Imagen.objects.filter(UsuarioSistema=request.user.id, is_predeterminado=True).exists():
                    getDataEstilo = Imagen.objects.get(UsuarioSistema=request.user.id, is_predeterminado=True)
                    getIdEstilo = getDataEstilo.id
                else: 
                    getIdEstilo = None
                
                print(f'valor de checkbox: {rememberCredentials}') 
                
                if rememberCredentials:
                    saveCredentials(request.user.id, usuarioCliente, contraseña)
                else:
                    deleteCredentials(request.user.id)
                      
                positions = request.POST['positions']
                positions_parse = json.loads(positions)
                
                
                if firma_lote:
                    
                    posición_multiple = positions_parse[0]
                        
                    x1 = int(float(posición_multiple.get('x1'))) - 5
                    x2 = int(float(posición_multiple.get('x2'))) - 5
                    y1 = int(float(posición_multiple.get('y1')))
                    y2 = int(float(posición_multiple.get('y2')))  
                    
                    find_documents = documentos.objects.get(secret=tokenEnvio)
                    
                    for nombre_documento, url_documento in zip(find_documents.nameArchivos, find_documents.url_archivos):
                    
                        insertFirmas = detalleFirma(
                            TokenAuth = tokenEnvio,
                            documento = url_documento,
                            nombre_documento = nombre_documento,
                            pagina = 1,
                            p_x1 = x1,
                            p_x2 = x2,
                            p_y1 = y1,
                            p_y2 = y2
                        )
                        insertFirmas.save()
                    
                else:
                    
                    for position in positions_parse:
                        
                        document_name = position.get('document_name')
                        parsed_url = urlparse(document_name)
                        filename_encoded = parsed_url.path
                        filename_decoded = unquote(filename_encoded)
                        name_document = filename_decoded
                        
                        x1 = int(float(position.get('x1'))) - 5
                        x2 = int(float(position.get('x2'))) - 5
                        y1 = int(float(position.get('y1')))
                        y2 = int(float(position.get('y2')))  
                    
                        insertFirmas = detalleFirma(
                            TokenAuth = tokenEnvio,
                            documento = position.get('document_url'),
                            nombre_documento = name_document,
                            pagina = position.get('page'),
                            p_x1 = x1,
                            p_x2 = x2,
                            p_y1 = y1,
                            p_y2 = y2
                        )
                        insertFirmas.save()
                                           
                    
                find_firmas = detalleFirma.objects.filter(TokenAuth=tokenEnvio)
                
                for firma in find_firmas:            
                    
                    coordenadasFirma = f'{firma.p_x1},{firma.p_y1},{firma.p_x2},{firma.p_y2}'
                    
                    tokenArchivo = secrets.token_urlsafe(50)
                    idFirma = signDocument(tokenEnvio, usuarioCliente, contraseña, pin, firma.nombre_documento, nameCarpeta, coordenadasFirma, str(int(firma.pagina)-1), tokenArchivo, getIdEstilo, firma.documento, request.user.id)
                    if idFirma == "error:Exception('Certificate not valid',)":
                        reasonError = "Certificado  de firma electrónica vencido"
                        messages.error(request, reasonError)
                        return redirect(new_url)
                    
                    
                    saveIDFile(firma.nombre_documento, tokenArchivo, tokenEnvio, "Pendiente", request.user.id, idFirma)
                    idsAPI.append(idFirma)
                    print(idFirma)   
                    time.sleep(0.5)
                
                
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
                    url_sign = "/firma_agil/signDocs/" + tokenEnvio
                    return redirect(url_sign)
                else:
                    messages.error(request, 'Error al Firmar. Por favor intentelo mas tarde.')
                    return redirect(new_url)
                    
        except Exception as e:
            url_sign = "/firma_agil/signDocs/" + tokenEnvio
            messages.error(request, f'Error al asignar las firmas: {e}')
            return redirect(url_sign)
        
        reasonError = translateResponse(validatePin)
        messages.error(request, reasonError)
        return redirect(new_url)
            
    else:
        
        try:
            isCkecked = credencialesCert.objects.get(user_system=request.user.id)
            user_cert = isCkecked.usuario_cert
            user_pass = isCkecked.pass_cert 
            isCkecked = True
        except ObjectDoesNotExist:
            isCkecked = False
            user_cert = ''
            user_pass = ''
        except Exception as e:
            print(f'Error al buscar las credenciales: {e}')
           
        try:
                    
            url_documentos = []
            find_documents = documentos.objects.get(secret=tokenEnvio)
            for documento in find_documents.url_archivos:
                url_documentos.append(documento)
                        
                    
            firmantes = []
            firmantes.append({"name": "Firma Electrónica", "id": "1"})
                    
                        
            contexto = {
                'pdf_files': url_documentos, 
                'firmantes': firmantes,
                'tokenEnvio': tokenEnvio,
                'usuario_cert': user_cert,
                'pass_cert': user_pass,
                'isChecked': isCkecked
            }
            
            if is_mobile(request):
                # return render(request, 'signbox/asignar_firma.html', contexto)    
                return render(request, 'signbox/asignar_firma _movil_devices.html', contexto)
            else:
                return render(request, 'signbox/asignar_firma.html', contexto)    
            
        except Exception as e:
            messages.error(request, f'Error al cargar documentos: {e}')
            return redirect(f'/firma_agil/uploadFiles')
        
def firma_lote(request, tokenEnvio):
    
    new_url = "/firma_agil/verifyDocs/" + tokenEnvio
    
    if request.method == 'POST':
        try:
            usuarioCliente = request.POST['userInput']
            contraseña = request.POST['userpsw']
            pin = request.POST['userpin']
            rememberCredentials = request.POST.get('save_credentials', 'off') == 'on'
            validatePin = verifyPin(usuarioCliente, contraseña, pin, request.user.id)
            
            dataDocuments = documentos.objects.get(secret=tokenEnvio)
            nameCarpeta = dataDocuments.nameCarpeta
            
            idsAPI = []
            idError = []
            idOK = []
            
            if validatePin == None:
                
                if Imagen.objects.filter(UsuarioSistema=request.user.id, is_predeterminado=True).exists():
                    getDataEstilo = Imagen.objects.get(UsuarioSistema=request.user.id, is_predeterminado=True)
                    getIdEstilo = getDataEstilo.id
                else: 
                    getIdEstilo = None
                
                print(f'valor de checkbox: {rememberCredentials}') 
                
                if rememberCredentials:
                    saveCredentials(request.user.id, usuarioCliente, contraseña)
                else:
                    deleteCredentials(request.user.id)
                      
                positions = request.POST['positions']
                positions_parse = json.loads(positions)
                
                for position in positions_parse:
                    
                    document_name = position.get('document_name')
                    parsed_url = urlparse(document_name)
                    filename_encoded = parsed_url.path
                    filename_decoded = unquote(filename_encoded)
                    name_document = filename_decoded
                    
                    x1 = int(float(position.get('x1'))) - 5
                    x2 = int(float(position.get('x2'))) - 5
                    y1 = int(float(position.get('y1')))
                    y2 = int(float(position.get('y2')))
                
                    insertFirmas = detalleFirma(
                        TokenAuth = tokenEnvio,
                        documento = position.get('document_url'),
                        nombre_documento = name_document,
                        pagina = position.get('page'),
                        p_x1 = x1,
                        p_x2 = x2,
                        p_y1 = y1,
                        p_y2 = y2
                    )
                    insertFirmas.save()
                    
                    
                find_firmas = detalleFirma.objects.filter(TokenAuth=tokenEnvio)
                
                for firma in find_firmas:            
                    
                    coordenadasFirma = f'{firma.p_x1},{firma.p_y1},{firma.p_x2},{firma.p_y2}'
                    
                    tokenArchivo = secrets.token_urlsafe(50)
                    idFirma = signDocument(tokenEnvio, usuarioCliente, contraseña, pin, firma.nombre_documento, nameCarpeta, coordenadasFirma, str(int(firma.pagina)-1), tokenArchivo, getIdEstilo, firma.documento, request.user.id)
                    saveIDFile(firma.nombre_documento, tokenArchivo, tokenEnvio, "Pendiente", request.user.id, idFirma)
                    idsAPI.append(idFirma)
                    print(idFirma)   
                    # time.sleep(1)
                
                
                while True:
                    
                    
                    registros_pendientes = VitacoraFirmado.objects.filter(IDArchivoAPI__in=idsAPI, EstadoFirma='Pendiente')
                     
                    if not registros_pendientes.exists():
                        print("Todos los estados han cambiado.")
                        break        
                    # time.sleep(1)
            
            
                # Validación de logs de firmado
                for id in idsAPI:
                    validateID = VitacoraFirmado.objects.get(IDArchivoAPI=id)
                    idOK.append(id) if validateID.EstadoFirma == "Firmado" else idError.append(id)
                    
                    
                if idOK:  
                    url_sign = "/firma_agil/signDocs/" + tokenEnvio
                    return redirect(url_sign)
                else:
                    messages.error(request, 'Error al Firmar. Por favor intentelo mas tarde.')
                    return redirect(new_url)
                    
        except Exception as e:
            url_sign = "/firma_agil/signDocs/" + tokenEnvio
            messages.error(request, f'Error al asignar las firmas: {e}')
            return redirect(url_sign)
        
        reasonError = translateResponse(validatePin)
        messages.error(request, reasonError)
        return redirect(new_url)
    else:
        
        try:
            isCkecked = credencialesCert.objects.get(user_system=request.user.id)
            user_cert = isCkecked.usuario_cert
            user_pass = isCkecked.pass_cert 
            isCkecked = True
        except ObjectDoesNotExist:
            isCkecked = False
            user_cert = ''
            user_pass = ''
        except Exception as e:
            print(f'Error al buscar las credenciales: {e}')
           
        try:
                    
            url_documentos = []
            find_documents = documentos.objects.get(secret=tokenEnvio)
            for documento in find_documents.url_archivos:
                url_documentos.append(documento)
                        
                    
            firmantes = []
            firmantes.append({"name": "Firma Electrónica", "id": "1"})
                    
                        
            contexto = {
                'pdf_files': url_documentos, 
                'firmantes': firmantes,
                'tokenEnvio': tokenEnvio,
                'usuario_cert': user_cert,
                'pass_cert': user_pass,
                'isChecked': isCkecked
            }

            return render(request, 'signbox/asignar_firma.html', contexto)
        except Exception as e:
            messages.error(request, f'Error al cargar documentos: {e}')
            return redirect(f'/firma_agil/uploadFiles')        

        
def convertir_x(x_obt):
    a_x = 0.84
    b_x = 1.6
    return round(a_x * x_obt + b_x)

def convertir_y(y_obt):
    a_y = 0.825
    b_y = -78.725
    return round(a_y * y_obt + b_y)

def validar_url(request):
    if request.method == 'POST':
        request_parse = json.loads(request.body)
        TokenAuth = request_parse.get('token_auth_archivo', None)
        
        try:
            get_documento_url = VitacoraFirmado.objects.get(TokenArchivo=TokenAuth)
            validar_link = validar_Link_Archivo(TokenAuth)
            
            if not validar_link == 'OK':
                get_documento_url.url_archivo = validar_link
                get_documento_url.save()
            
            get_documento_url = VitacoraFirmado.objects.get(TokenArchivo=TokenAuth)
            
            return JsonResponse({"success": True, "url": get_documento_url.url_archivo}, status=200)            
        except Exception as e:
            return JsonResponse({"success": False, "error": e})
        
def validación_licencia(usuarioID):
    try:
        validate_perfil = PerfilSistema.objects.get(usuario=usuarioID)
        if validate_perfil.empresa == None:
            validate_user = UsuarioSistema.objects.get(UsuarioGeneral=usuarioID)
            validate_licencia = LicenciasSistema.objects.filter(usuario=validate_user.id, tipo='Firma Agil').order_by('-id').last()
        else:            
            validate_licencia = LicenciasSistema.objects.filter(empresa=validate_perfil.empresa.id, tipo='Firma Agil').order_by('-id').last()
            
            
        if validate_licencia.licencia_vencida():
            return json.dumps({"success": False, "error": "Licencia Expirada"})
            
        if int(validate_licencia.porcentaje) >= 100:
            return json.dumps({"success": False, "error": "Creditos Agotados"})
        else: 
            return json.dumps({"success": True, "data": "OK", "tipo_licencia": validate_licencia.env, "id_licencia": validate_licencia.id})                

    except Exception as e:
        print(e)
        return json.dumps({"success": False, "error": "No se ha podido encontrar su licencia"})