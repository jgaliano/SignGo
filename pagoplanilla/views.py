from django.shortcuts import render, redirect
import os
from django.core.files.storage import default_storage
from django.conf import settings
from django.http import JsonResponse, HttpResponse
import secrets
import random
import csv
from .models import Contacto, ListaContactos, Plantilla, Empresa, PerfilUsuario, Envios, VitacoraEnvios
import pandas as pd
import json
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from xhtml2pdf import pisa
from django.template import Context
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.core.mail import send_mail
import time
from django.utils import timezone
import requests
from django.contrib import messages
from signbox.models import billingSignboxProd, billingSignboxSandbox, signboxAPI
from webhook.models import webhookIP
from django.contrib.auth.models import User, Group
from webhook.models import webhookIP
from django.utils.dateparse import parse_date
import io
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
import zipfile

# Create your views here.
def helloworld(request):
    return render(request, 'planilla/helloworld.html')

def plantilla(request):
    if request.method == 'POST':
        try:
            # Lee el cuerpo de la solicitud como JSON
            data = json.loads(request.body)
            contenido = data.get('contenido', None)
            
            getIdUser = request.user.id
            getPerfil = PerfilUsuario.objects.get(usuario=getIdUser)
            getEmpresa = Empresa.objects.get(id=getPerfil.empresa.id)
            
            if contenido:
                # insertPlantilla = Plantilla(
                #     Nombre = "Prueba",
                #     Contenido = contenido,
                #     Empresa = getEmpresa
                # )
                # insertPlantilla.save()
                UpdatePlantilla = Plantilla.objects.get(id=10)
                UpdatePlantilla.Contenido = contenido
                UpdatePlantilla.save()
            else:
                print("El contenido no fue recibido o está vacío.")
            
            # Respuesta de éxito
            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            print("Error al decodificar el JSON.")
            return JsonResponse({'success': False, 'error': 'Error al decodificar el JSON.'})
    # return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    contexto = {
        'nombre_trabajador': 'Jhonatan Galiano',
        'cargo_trabajador': 'Programador',
        'departamento': 'Firma-E'
    }
    return render(request, 'planilla/plantilla.html')

def contactos(request):
    getListaContactos = ListaContactos.objects.all().order_by('-id')
    contexto = {
        'Contactos': getListaContactos
    }
    return render(request, 'planilla/contactos.html', contexto)

def subir_csv(request):
    if request.method == 'POST' and request.FILES.get('archivo_csv'):
        archivo_csv = request.FILES['archivo_csv']
        nombreLista = request.POST.get('nombre_lista')
        
        tokenAuth = random.randint(10**14, 10**15 - 1)  
        
        getIdUser = request.user.id
        getPerfil = PerfilUsuario.objects.get(usuario=getIdUser)
        getEmpresa = Empresa.objects.get(id=getPerfil.empresa.id)        
        
        
        
        
        subcarpeta = 'pagoPlanilla/contactos/'
        rutaCarpeta = os.path.join(settings.MEDIA_ROOT, subcarpeta, str(tokenAuth))
        
        os.makedirs(rutaCarpeta)
        
        ruta_archivo = os.path.join(rutaCarpeta, archivo_csv.name)

        with default_storage.open(ruta_archivo, 'wb+') as destino:
            for chunk in archivo_csv.chunks():
                destino.write(chunk)
                
        valor = saveContacts(rutaCarpeta, archivo_csv.name, str(tokenAuth))
        
        insertLIsta = ListaContactos(
            nombre = nombreLista,
            tokenAuth = tokenAuth,
            Empresa = getEmpresa,
            CantidadContactos = valor
        )
        insertLIsta.save()

        return JsonResponse({'success': True, 'ruta': ruta_archivo})
    return JsonResponse({'success': False})


def saveContacts(rutaCarpeta, archivo_csv, tokenAuth):
    csv_file_path = f"{rutaCarpeta}/{archivo_csv}"
    
    if not os.path.exists(csv_file_path):
        return HttpResponse("El archivo CSV no se encuentra.")
    try:
        df = pd.read_csv(csv_file_path, sep=';')
        nombres = []
        print(df.columns)
        df.columns = df.columns.str.strip()
        for index, row in df.iterrows():
            contactos = {
                'Nombres': row['Nombres'],
                'Apellidos': row['Apellidos'],
                'Email': row['Email'],
                'Celular': row['Celular'],
                'Salario': row['Salario'],
                'Departamento': row['Departamento'],
                'Puesto': row['Puesto'],
                'Periodo': row['Periodo'],
                'tokenAuth': tokenAuth
            }
            nombres.append(contactos)
        
        print(nombres)
            
        for contacto in nombres:   
            insertData = Contacto(
                Nombres = contacto['Nombres'],
                Apellidos = contacto['Apellidos'],
                Email = contacto['Email'],
                Celular = contacto['Celular'],
                Salario = contacto['Salario'],
                Departamento = contacto['Departamento'],
                Puesto = contacto['Puesto'],
                Periodo = contacto['Periodo'],
                tokenAuth = contacto['tokenAuth'],
            )
            insertData.save()
            
        cantidadContactos = len(nombres)
        return cantidadContactos
    except Exception as e:
            print(f"Error: {e}")


def generar_boleta_pdf(request, tokenCarpeta, idUsuario):
    
    getDataUser = Contacto.objects.get(id=idUsuario)

    # Obtener la plantilla del modelo
    getPlantilla = Plantilla.objects.get(id=10)
    contenido = getPlantilla.Contenido
    
    ruta_archivo = os.path.join(settings.BASE_DIR, 'pagoplanilla', 'templates', 'planilla', 'plantillaPDF.html')
    with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
        archivo.write(contenido)
        print('El fragmento HTML ha sido guardado con éxito.')

    
    # Generar el contexto con las variables dinámicas
    contexto = {
        'nombre_trabajador': getDataUser.Nombres,
        'apellidos_trabajador': getDataUser.Apellidos,
        'cargo_trabajador': getDataUser.Puesto,
        'email_trabajador': getDataUser.Email,
        'celular_trabajador': getDataUser.Celular,
        'salario_trabajador': getDataUser.Salario,
        'departamento_trabajador': getDataUser.Departamento,
        'puesto_trabajador': getDataUser.Puesto
    }

    # Renderizar la plantilla HTML con el contexto
    html_renderizado = render_to_string('planilla/plantillaPDF.html', contexto)

    # Crear directorios si no existen
    ruta_directorio = os.path.join(settings.MEDIA_ROOT, f'pagoPlanilla/boletas/{tokenCarpeta}')
    os.makedirs(ruta_directorio, exist_ok=True)
    ruta_directorio_usuario = os.path.join(ruta_directorio, str(idUsuario))
    os.makedirs(ruta_directorio_usuario, exist_ok=True)

    # Definir la ruta del archivo PDF
    pdf_path = os.path.join(ruta_directorio_usuario, 'boleta_de_pago.pdf')

    # Generar el archivo PDF
    with open(pdf_path, 'wb') as pdf_file:
        pisa_status = pisa.CreatePDF(html_renderizado, dest=pdf_file)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=400)

    return HttpResponse(f'PDF generado y guardado en: {pdf_path}')

def envios(request):
    try:
        getEmpresa = PerfilUsuario.objects.get(usuario=request.user.id)
        
        getPlantillas = Plantilla.objects.filter(Empresa=getEmpresa.empresa.id)
        getContactos = ListaContactos.objects.filter(Empresa=getEmpresa.empresa.id)
        
        contexto = {
            'plantillas': getPlantillas,
            'contactos': getContactos    
        }
        return render(request, 'planilla/envios.html', contexto)
    except Exception as e:
        print(f'Error: {e}')
        messages.warning(request, e)
        
    if request.method == 'POST':
        try:
            requestContacto = request.POST['selectContacto']
            requestPlantilla = request.POST['selectPlantilla']
            requestName = request.POST['nameEnvio']
            requestAsunto = request.POST['inputAsunto']
            
            getIdLista = ListaContactos.objects.get(id=requestContacto)
            tokenLista = getIdLista.tokenAuth
            
            tokenEnvio = secrets.token_urlsafe(25)
            getIdEmpresa = PerfilUsuario.objects.get(usuario=request.user.id)
                
            insertDataEnvio = Envios(
                Plantilla = Plantilla.objects.get(id=requestPlantilla),
                ListaContactos = ListaContactos.objects.get(id=requestContacto),
                TokenAuth = tokenEnvio,
                Empresa = Empresa.objects.get(id=getIdEmpresa.empresa.id),
                NombreEnvio = requestName,
                UsuarioRemitente = getIdEmpresa
            )
            insertDataEnvio.save()
            
            getContactosEnviar = Contacto.objects.filter(tokenAuth=tokenLista)

            for doc in getContactosEnviar:
                generar_boleta_pdf(request, tokenLista, doc.id)
                sendCorreUsuario(request, doc.Email, doc.Nombres, tokenLista, doc.id, insertDataEnvio, tokenEnvio, getIdLista.tokenAuth, doc.Apellidos, requestAsunto)
                
            insertDocuments = Envios.objects.get(TokenAuth=tokenEnvio)
            insertDocuments.TotalEnvios = len(getContactosEnviar)
            insertDocuments.save()
            
            reasonError = f'{insertDocuments.TotalEnvios} Correos Enviados con Exito'
            messages.success(request, reasonError)
            return redirect('/planilla/envios')
        except Exception as e:
            reasonError = f'Error: {e}'
            messages.warning(request, reasonError)
            return redirect('/planilla/envios/')        
    
    return render(request, 'planilla/envios.html')

def sendCorreUsuario(request, correo, nombre, token, id, objectEnvio, tokenEnvio, tokenAuthLista, apellidos, asuntoCorreo):
        correo_electronico = correo

        remitente = 'noreply@signgo.online'  # Dirección de correo del remitente
        destinatario = correo_electronico # obtener correo de sesión del usuario
        asunto = asuntoCorreo
        
        getIpDominio = webhookIP.objects.get(id=1)
        
        tokenAuthEnvio = secrets.token_urlsafe(50)
        
        url = f'http://{getIpDominio.ip}/planilla/verifyDocs/{token}/{id}/{tokenAuthEnvio}'
        
        
        context = {
            'data': url,
            'nombre': f"{nombre} {apellidos}",
            'asunto': asuntoCorreo
        }
            
        template_html = render_to_string('planilla/plantillaCorreo.html', context)
            
        try:
            send_mail(
                asunto,  # Asunto del correo
                '',  # Contenido del correo
                remitente,  # Correo del remitente
                [destinatario],  # Lista de destinatarios
                fail_silently=False,  # Si se establece en True, los errores no se levantarán sino que se registrarán en la consola
                html_message=template_html
            )
            
            
            getObjectEnvio = Envios.objects.get(TokenAuth=tokenEnvio)
            
            nombreUsuario = f"{nombre} {apellidos}"
            
            insertVitacora = VitacoraEnvios(
                nombre = nombreUsuario,
                remitente = PerfilUsuario.objects.get(id=getObjectEnvio.UsuarioRemitente.id),
                empresa = Empresa.objects.get(id=getObjectEnvio.Empresa.id),
                token = tokenAuthEnvio,
                envioVitacora = getObjectEnvio,
                status = "Pendiente de Firma",
                tokenAuthLista = token,
                idUsuario = Contacto.objects.get(id=id)
            )
            insertVitacora.save()
            
            return print("Correo enviado")
        except Exception as e:
            print(f"Error al enviar el correo: {e}")
            
            

def verifyDocs(request, token, request_id, secretToken):
    getNombreUsuario = Contacto.objects.get(id=request_id)
    NombreUsuario = f'{getNombreUsuario.Nombres} {getNombreUsuario.Apellidos}'
    nameDocument = 'boleta_de_pago.pdf'
    viewDocuments = []
    viewDocuments.append([nameDocument, NombreUsuario])
    
    if request.method == "POST":
        try:
            usuarioCliente = request.POST['inputUsuario']
            contraseña = request.POST['inputContraseña']
            pin = request.POST['inputPin']
            coordenadas = '300,100,550,150'
            pagina = "0"
        
            
            validatePin = verifyPin(usuarioCliente, contraseña, pin)
            
            if validatePin == None:
                
                signDocument(request_id, usuarioCliente, contraseña, pin, nameDocument, token, coordenadas, pagina)
                updateSign = VitacoraEnvios.objects.get(token=secretToken)
                updateSign.status = "Firmado" # 1 es igual a firmado | 0 es igual a pendiente
                updateSign.scratchcard = usuarioCliente
                updateSign.fechaFirma = timezone.now() # Asigna fecha y hora de firmado
                updateSign.save()
                time.sleep(3)
                
                
                url_sign = f'/planilla/signDocs/{token}/{request_id}/{secretToken}'
                return redirect(url_sign)

            new_url = f'/planilla/verifyDocs/{token}/{request_id}/{secretToken}'
            reasonError = translateResponse(validatePin)
            messages.error(request, reasonError)
            return redirect(new_url)
        except Exception as e:
            reasonError = f'Error: {e}'
            messages.error(request, reasonError)
            return redirect(new_url)
    
    
    getStatusFirma = VitacoraEnvios.objects.get(token=secretToken)
    
    contexto = {
        'documentos': viewDocuments,
        'carpeta': token,
        'id': request_id,
        'status': getStatusFirma.status,
        'secretToken': secretToken
    } 

    return render(request, "planilla/sign.html", contexto)
    
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
        'Token locked': lambda: "Codigo PIN Bloqueado"
    }
    return switcher.get(data, lambda: data)()

def signDocument(id_user, usuarioCliente, contraseña, pin, nombreDocumento, nameCarpeta, coordenadas, pagina):
    
    getDataWebhook = webhookIP.objects.get(id=1)
    
    if getDataWebhook.protocol == "1":
        protocolo = "https"
    else:
        protocolo = "http"
    
    dataUrlOut = protocolo + "://" + getDataWebhook.ip + "/webhook/resultPlanilla/" + nameCarpeta + "/" + id_user + "/" + nombreDocumento
    dataUrlBack = protocolo + "://" + getDataWebhook.ip + "/webhook/services/registros"
    
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

    payload = {
        'url_out': dataUrlOut,
        'urlback': dataUrlBack,
        'env': 'sandbox',
        'format': 'pades',
        'username': usuarioCliente,
        'password': contraseña,
        'pin': pin,
        'level': 'BES',
        'billing_username': userBilling,
        'billing_password': passBilling,
        'identifier': 'DS0',
        'reason': 'Firma Demo',
        'location': 'Guatemala, Guatemala',
        'position': coordenadas,
        'npage': pagina,
        'paragraph_format': '[{"font": ["Universal-Italic", 10],"align": "right","data_format": {"timezone": "America/Guatemala","strtime": "%d/%m/%Y %H:%M:%S%z"},"format": ["Firmado por: $(CN)s","Ciudad de Guatemala, $(C)s","Fecha: $(date)s"]}]'
    }
    
    urlArchivos = './media/pagoPlanilla/boletas/' + nameCarpeta + "/" + id_user + "/"
    ruta_archivo = os.path.join(urlArchivos, nombreDocumento)
    
    files = {
        'file_in': ('PruebaFirma.pdf', open(ruta_archivo, 'rb')),
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(url, data=payload, files=files)
    print(response.text)
    return "Send Success"
    
def verifySignDocs(request, tokenSign, request_id, secretToken):
    nombreFile = "boleta_de_pago.pdf"
    viewDocuments = []
    
    try:
        getVitacora = VitacoraEnvios.objects.get(token=secretToken)
        statusEnvio = getVitacora.status
        nombreUsuario = getVitacora.nombre
        fechaFirmado = getVitacora.fechaFirma
        IdAuthEnvio = getVitacora.envioVitacora.TokenAuth
        viewDocuments.append([nombreFile, '310KB', statusEnvio, nombreUsuario, fechaFirmado ])
    except Exception as e:
        print(f'Error: {e}')
    
    contexto = {
        'documentos': viewDocuments,
        'carpeta': tokenSign,
        'id': request_id,
        'IdAuth': IdAuthEnvio
    } 
    
    return render(request, "planilla/firmados.html", contexto)

def empresas(request):
    
    if request.method == 'POST':
        # Filtros de busqueda 
        nombre_empresa = request.POST.get('nombreEmpresa')
        nit = request.POST.get('nit')
        ciudad = request.POST.get('ciudad')
        fecha_desde = request.POST.get('fechaRegistroDesde')
        fecha_hasta = request.POST.get('fechaRegistroHasta')
        estado = request.POST.get('estado')
        
        resultados = Empresa.objects.all()
        
        if nombre_empresa:
            resultados = resultados.filter(Nombre__icontains=nombre_empresa)
        if nit:
            resultados = resultados.filter(NIT__icontains=nit)
        if ciudad:
            resultados = resultados.filter(Ciudad__icontains=ciudad)
        if fecha_desde:
            resultados = resultados.filter(FechaRegistro__gte=fecha_desde)
        if fecha_hasta:
            resultados = resultados.filter(FechaRegistro__lte=fecha_hasta)
        if estado:
            resultados = resultados.filter(Estado=estado)
        contexto = {
            'Empresas': resultados
        }
        return render(request, 'planilla/empresas.html', contexto)
    else: 
        resultados = Empresa.objects.all().order_by('-id')[:50]
        contexto = {
            'Empresas': resultados
        }
        return render(request, 'planilla/empresas.html', contexto)

def crearEmpresa(request):
    if request.method == 'POST':
        NombreEmpresa = request.POST['nombreEmpresa']
        NitEmpresa = request.POST['nit']
        CiudadEmpresa = request.POST['ciudad']
        SectorEmpresa = request.POST['sector']
        EstadoEmpresa = request.POST['estado']
        TokenAuthEmpresa = secrets.token_urlsafe(30)
        InsertEmpresa = Empresa(
            Nombre = NombreEmpresa,
            NIT = NitEmpresa,
            Ciudad = CiudadEmpresa,
            Sector = SectorEmpresa,
            Estado = EstadoEmpresa,
            TokenAuth = TokenAuthEmpresa,
        )
        InsertEmpresa.save()
        return redirect('/planilla/crearEmpresa/')
    return render(request, 'planilla/crearEmpresa.html')


def admin(request):
    try:
        getIdEmpresa = PerfilUsuario.objects.get(usuario=request.user.id)    
        getUsers = PerfilUsuario.objects.filter(empresa=getIdEmpresa.empresa)
        
        contexto = {
            'Usuarios': getUsers
        }
        return render(request, 'planilla/signbolAdmin_Cliente.html', contexto)
    except Exception as e:
         messages.warning(request, e)
         return render(request, 'planilla/signbolAdmin_Cliente.html')
         

def signbolCrearuser(request):
    if request.method == 'POST': 
        nameUser = request.POST['nombreUsuario']
        empresaUser = request.POST['nombreEmpresa']
        emailUser = request.POST['email']
        psw1User = request.POST['psw1']
        psw2User = request.POST['psw2']           
    
        # Validación inicial: verificar si el usuario o el correo ya existen
        if User.objects.filter(username=nameUser).exists():
            messages.error(request, "El usuario ya existe en el sistema")
            return redirect('/planilla/crearUsuario/')
        elif User.objects.filter(email=emailUser).exists():
            messages.error(request, "El correo ya existe en el sistema")
            return redirect('/planilla/crearUsuario/')

        idEmpresa = None
        if 'isEmpresa' in request.POST:
            empresa_exists = Empresa.objects.filter(Nombre=empresaUser).exists()
            print(f'estado de busqueda de empresa: {empresa_exists}')
            if not empresa_exists:
                messages.error(request, "La empresa ingresada no existe")
                return redirect('/planilla/crearUsuario/')
            idEmpresa = Empresa.objects.get(Nombre=empresaUser)

        # Validación de contraseñas
        if psw1User != psw2User:
            messages.error(request, "Las contraseñas no coinciden")
            return redirect('/planilla/crearUsuario/')
        
        user = User.objects.create_user(username=nameUser, email=emailUser, password=psw1User)
        token = secrets.token_urlsafe(45)

        grupos = {
            'is_signbox': 'SignboxAuth',
            'is_oneshot': 'OneshotAuth',
            'is_vol': 'VolAuth',
            'is_4identity': '4identityAuth',
            'is_esign': 'eSignAuth',
            'is_signbol': 'SignbolAuth',
            'is_plantilla': 'planillaAuth',
            'is_contacto': 'SignbolContactosAuth',
            'is_envio': 'SignbolEnviosAuth',
            'is_reportes': 'SignbolReportesAuth',
            'is_AdminSignbol': 'SignbolAdminAuth',
        }

        for key, group_name in grupos.items():
            group = Group.objects.get(name=group_name)
            if key in request.POST:
                user.groups.add(group)
            
        user.save()

        userProfile = PerfilUsuario(
            empresa=idEmpresa,
            usuario=user,
            tokenAuth=token
        )
        userProfile.save()
        messages.success(request, "Usuario creado con éxito")
        return redirect('/planilla/usersSignbol/')


    getEmpresas = Empresa.objects.all()
    listaEmpresas = []
    for empresa in getEmpresas:
        listaEmpresas.append(empresa.Nombre)

    return render(request, 'planilla/signbolCrearUser.html', {'empresas': listaEmpresas})

def buscar_empresas(request):
    query = request.GET.get('q', '')
    if query:
        empresas = Empresa.objects.filter(Nombre__icontains=query)
        resultados = [{'id': empresa.id, 'nombre': empresa.Nombre} for empresa in empresas]
        return JsonResponse({'empresas': resultados})
    return JsonResponse({'empresas': []})

def usersSignbol(request):
    getPerfiles = PerfilUsuario.objects.all()
    contexto = {
        'Perfiles': getPerfiles
    }
    return render(request, 'planilla/signbol_AdminUser.html', contexto)

def usersCreate(request):
    return render(request, 'planilla/signbol_AdminCreateUser.html')

def reportes(request):
    if request.method == "POST":
        enviosHistory = Envios.objects.all()
    
        nombre_receptor = request.POST.get('nombreEmpresa', '')
        fecha_desde = request.POST.get('fechaRegistroDesde', '')
        fecha_hasta = fecha_hasta = request.POST.get('fechaRegistroHasta', '')
        
        if nombre_receptor:
            enviosHistory = enviosHistory.filter(NombreEnvio__icontains=nombre_receptor)
    
        if fecha_desde:
            enviosHistory = enviosHistory.filter(fechaEnvio__date__gte=fecha_desde)
        
        if fecha_hasta:
            enviosHistory = enviosHistory.filter(fechaEnvio__date__lte=fecha_hasta)
            
        contexto = {
            'Envios': enviosHistory,
            'FiltroNombre': nombre_receptor,
            'FiltroDesde': fecha_desde,
            'FiltroHasta':fecha_hasta
        }
        
        return render(request, 'planilla/signbolReportes.html', contexto)
    else: 
        try:
            getIdEmpresa = PerfilUsuario.objects.get(usuario=request.user.id)
            getEnvios = Envios.objects.filter(Empresa=getIdEmpresa.empresa.id).order_by('-id')
            
            contexto = {
                'Envios': getEnvios
            }
            return render(request, 'planilla/signbolReportes.html', contexto)
        except Exception as e:
            messages.warning(request, e)
            return render(request, 'planilla/signbolReportes.html')

def EditUsuarioSignbol(request, token):
    
    if PerfilUsuario.objects.filter(tokenAuth=token).exists():
        getUsuario = PerfilUsuario.objects.get(tokenAuth=token)
    else:
        return redirect('/acceso-denegado/')
    
    contexto = {
        'Usuario': getUsuario
    }

    if request.method == 'POST':
        nameUser = request.POST['nombreUsuario']
        empresaUser = request.POST['empresaUser']
        emailUser = request.POST['email']
        psw1User = request.POST['psw1']
        
        getNameUser = PerfilUsuario.objects.get(tokenAuth=token)
        
        if getNameUser.usuario.username != nameUser and User.objects.filter(username=nameUser).exclude(username=getNameUser.usuario.username).exists():
            reasonError = "El usuario ya existe en el sistema"
            messages.error(request, reasonError)
            return redirect(f'/planilla/EditUsuarioSignbol/{token}')

        if getNameUser.usuario.email != emailUser and User.objects.filter(email=emailUser).exclude(email=getNameUser.usuario.email).exists():
            reasonError = "El correo ya existe en el sistema"
            messages.error(request, reasonError)
            return redirect(f'/planilla/EditUsuarioSignbol/{token}')

        if empresaUser and not Empresa.objects.filter(Nombre=empresaUser).exists():
            reasonError = "La empresa ingresada no existe"
            messages.error(request, reasonError)
            return redirect(f'/planilla/EditUsuarioSignbol/{token}')
        
        getDataUser = PerfilUsuario.objects.get(tokenAuth=token)
        getUser = User.objects.get(id=getDataUser.usuario.id)
        
        if psw1User:
            getUser.set_password(psw1User)
        
        if empresaUser:
            getEmpresa = Empresa.objects.get(Nombre=empresaUser)
            getDataUser.empresa = getEmpresa
            getDataUser.save()
        
        getUser.username = nameUser
        getUser.email = emailUser    
        getUser.save()
        
        reasonError = "Usuario Actualizado con Éxito"
        messages.success(request, reasonError)
        return redirect('/planilla/usersSignbol')
    
    return render(request, 'planilla/signbol_EditUser.html', contexto)


def envio(request, token):
    
    if request.method == 'POST':
        getIdEnvio = Envios.objects.get(TokenAuth=token)
        enviosHistory = VitacoraEnvios.objects.filter(envioVitacora=getIdEnvio.id)
        
        nombreReceptor = request.POST['nombreReceptor']
        fecha_desde = request.POST['fechaRegistroDesde']
        fecha_hasta = request.POST['fechaRegistroHasta']
        statusFirma = request.POST['selectStatus']
        
        if nombreReceptor:
            enviosHistory = enviosHistory.filter(nombre__icontains=nombreReceptor)
    
        if fecha_desde:
            enviosHistory = enviosHistory.filter(fechaEnvio__date__gte=fecha_desde)
        
        if fecha_hasta:
            enviosHistory = enviosHistory.filter(fechaEnvio__date__lte=fecha_hasta)
            
        if statusFirma == 'Firmado' or statusFirma == 'Pendiente de Firma':
            enviosHistory = enviosHistory.filter(status__icontains=statusFirma)
        else: 
            statusFirma = 'none'
       
        getEnvio = Envios.objects.get(TokenAuth=token)
        getFilesSigned = VitacoraEnvios.objects.filter(envioVitacora=getEnvio.id, status="Firmado").count()
            
        contexto = {
            'NombreEnvio': getEnvio,
            'Envio': enviosHistory,
            'TokenAuth': token,
            'FilesSigned': getFilesSigned,
            'FiltroReceptor': nombreReceptor,
            'FiltroDesde': fecha_desde,
            'FiltroHasta': fecha_hasta,
            'FiltroStatus': statusFirma
        }
        
        return render(request, 'planilla/ReporteEnvio.html', contexto)
    
    getEnvio = Envios.objects.get(TokenAuth=token)
    getVitacora = VitacoraEnvios.objects.filter(envioVitacora=getEnvio.id)
    getFilesSigned = VitacoraEnvios.objects.filter(envioVitacora=getEnvio.id, status="Firmado").count()
    
    contexto = {
        'NombreEnvio': getEnvio,
        'Envio': getVitacora,
        'FilesSigned': getFilesSigned,
        'TokenAuth': token
    }
    return render(request, 'planilla/ReporteEnvio.html', contexto)

def detalleContacto(request, token):
    try:  
        getContactos = Contacto.objects.filter(tokenAuth=token)
        getNombreLista = ListaContactos.objects.get(tokenAuth=token)
        
        contexto = {
            'contactos': getContactos,
            'nombre_lista': getNombreLista.nombre
        }
        return render(request, 'planilla/detalleContacto.html', contexto)
    except Exception as e: 
        reasonError = e
        messages.warning(request, reasonError)
        return render(request, 'planilla/detalleContacto.html')
    
    
def generar_reporte_pdf(request):
    nombre_receptor = request.POST.get('nombreEmpresa', '')
    fecha_desde = request.POST.get('fechaRegistroDesde', '')
    fecha_hasta = request.POST.get('fechaRegistroHasta', '')
    
    enviosHistory = Envios.objects.all()
    
    now_utc = timezone.now()
    now_utc_minus_6 = now_utc - timedelta(hours=6)
    
    if nombre_receptor:
        enviosHistory = enviosHistory.filter(NombreEnvio__icontains=nombre_receptor)
    
    if fecha_desde:
        enviosHistory = enviosHistory.filter(fechaEnvio__date__gte=fecha_desde)
        
    if fecha_hasta:
        enviosHistory = enviosHistory.filter(fechaEnvio__date__lte=fecha_hasta)

    contexto = {
        'Envios': enviosHistory,
        'current_date': now_utc_minus_6
    }
    archivo = 'reporteEnvios.html'
        
    getPDF = make_pdf(archivo, contexto)       
    response = getPDF
    return response

def reporteDetalleEnvio(request, token):
    getIdEnvio = Envios.objects.get(TokenAuth=token)
    enviosHistory = VitacoraEnvios.objects.filter(envioVitacora=getIdEnvio.id)
        
    nombre_receptor = request.POST.get('nombreReceptor', '')
    fecha_desde = request.POST.get('fechaRegistroDesde', '')
    fecha_hasta = request.POST.get('fechaRegistroHasta', '')
    select_status = request.POST.get('selectStatus', '')
        
    now_utc = timezone.now()
    now_utc_minus_6 = now_utc - timedelta(hours=6)
        
    if nombre_receptor:
        enviosHistory = enviosHistory.filter(nombre__icontains=nombre_receptor)
        
    if fecha_desde:
        enviosHistory = enviosHistory.filter(fechaEnvio__date__gte=fecha_desde)
            
    if fecha_hasta:
        enviosHistory = enviosHistory.filter(fechaEnvio__date__lte=fecha_hasta)
            
    if select_status == 'Firmado' or select_status == 'Pendiente de Firma':
        enviosHistory = enviosHistory.filter(status__icontains=select_status)


    contexto = {
        'Envios': enviosHistory,
        'current_date': now_utc_minus_6,
        'NombreEnvio': getIdEnvio.NombreEnvio
    }
    archivo = 'reporteDetalleEnvio.html'
            
    getPDF = make_pdf(archivo, contexto)       
    response = getPDF
    return response
    
    


def make_pdf(archivo, contexto):

    html_renderizado = render_to_string(f'reportes/{archivo}', contexto)
    
    pdf_buffer = io.BytesIO()
    
    pisa_status = pisa.CreatePDF(html_renderizado, dest=pdf_buffer)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=400)

    pdf_buffer.seek(0)  # Asegurarse de estar al inicio del archivo
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="boleta_de_pago.pdf"'

    return response

@csrf_exempt
def reenviarCorreo(request, token):
    if request.method == 'POST':
        data = json.loads(request.body)
        tokenAuth = data.get('tokenAuth', [])
        seleccionados = data.get('seleccionados', [])
        
        for envio_id in seleccionados:
            getEnvio = VitacoraEnvios.objects.get(id=envio_id)
            getContacto = Contacto.objects.get(id=getEnvio.idUsuario.id)
            SendReenvio(request, getContacto.Email, getEnvio.nombre, getContacto.tokenAuth, getEnvio.idUsuario.id, "Correo Para Firma", getEnvio.token)
            print(f'Correo enviado: {envio_id}')
            pass
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)



def SendReenvio(request, correo, nombre, token, id, asuntoCorreo, tokenVitacoraEnvio):
        correo_electronico = correo
        remitente = 'noreply@signgo.online'  # Dirección de correo del remitente
        destinatario = correo_electronico # obtener correo de sesión del usuario
        asunto = asuntoCorreo
        getIpDominio = webhookIP.objects.get(id=1)
        tokenAuthEnvio = tokenVitacoraEnvio
        
        url = f'http://{getIpDominio.ip}/planilla/verifyDocs/{token}/{id}/{tokenAuthEnvio}'
        
        context = {
            'data': url,
            'nombre': nombre,
            'asunto': asuntoCorreo
        }
            
        template_html = render_to_string('planilla/plantillaCorreo.html', context)
            
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



def UI_prueba_plantilla(request):
    return render(request, 'planilla/UI_prueba_plantilla.html')

@csrf_exempt
def descargarArchivos(request, token):
    if request.method == 'POST':
        data = json.loads(request.body)
        tokenAuth = data.get('tokenAuth')
        seleccionados = data.get('seleccionados', [])
        print(seleccionados)
        
        if not seleccionados:
            return HttpResponse("No se seleccionaron archivos", status=400)

        file_paths = []
        
        for seleccionado in seleccionados:
            try:
                GetIdVitacora = VitacoraEnvios.objects.get(id=seleccionado)
                if GetIdVitacora.status == 'Firmado':
                    GetIdContacto = Contacto.objects.get(id=GetIdVitacora.idUsuario.id)
                    print(f'{GetIdContacto.tokenAuth}/{GetIdVitacora.idUsuario.id}')
                    file_path = os.path.join(
                        settings.MEDIA_ROOT, 
                        f'pagoPlanilla/boletasSign/{GetIdContacto.tokenAuth}/{GetIdVitacora.idUsuario.id}/boleta_de_pago.pdf'
                    )
                    new_name = f'archivo_{GetIdVitacora.nombre}.pdf'
                    file_paths.append((file_path, new_name))
            except (VitacoraEnvios.DoesNotExist, Contacto.DoesNotExist):
                # archivo no existe
                continue

        zip_filename = "archivos.zip"
        response = HttpResponse(content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{zip_filename}"'

        with zipfile.ZipFile(response, 'w') as zip_file:
            for file_path, new_name in file_paths:
                if os.path.exists(file_path):
                    zip_file.write(file_path, arcname=new_name)

        print('Zip generado con éxito')
        return response

    return HttpResponse("Método no permitido", status=405)
    
    