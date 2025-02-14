import json
from django.forms import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from django.contrib import messages
import requests
from oneshot.models import billingOneshotProd, billingOneshotSandbox, oneshotAPI
from signbox.models import billingSignboxProd, billingSignboxSandbox, signboxAPI
from vol.models import volIP
from . models import PerfilSistema, UsuarioSistema, EmpresaSistema, LicenciasSistema, RenovacionLicencia, CompraExtraordinaria, token_oneshot
from webhook.models import webhookIP
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpRequest
from django.template.loader import render_to_string
from django.core.mail import send_mail
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import os
import secrets
from django.core.exceptions import ObjectDoesNotExist

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_invalid(self, form):
        messages.error(self.request, "Credenciales inválidas. Por favor, inténtelo de nuevo.")
        return super().form_invalid(form)

# Create your views here.
@login_required
def helloworld(request):
    if request.method == "POST":
        try:
            asunto = "Prueba de envío de correo con Amazon SES"
            mensaje = "Este es un mensaje enviado desde Django usando Amazon SES."
            remitente = "notificaciones@signgo.com.gt"
            destinatarios = ["jgaliano@ccg.gt"]
            send_mail(asunto, mensaje, remitente, destinatarios)
            messages.success(request, 'Correo Enviado con Éxito')
            return redirect('/helloworld/')
        except Exception as e:
            messages.error(request, f"Error al enviar el correo: {e}")
            return redirect('/helloworld/')
        
    host = request.get_host()
    contexto = {'host': host}
    return render(request, 'helloworld.html', contexto)


     # URLs prefirmadas para los documentos
    # pdf_files = [
    #     "https://signgo-bucket.s3.amazonaws.com/media/signbox/FilesNoFirmados/466432435317699/prueba_varias_paginas.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA45XFJQA2SMB73TVY%2F20241208%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20241208T224010Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=d2cc448891d69fc2e7927233e8d4f06e7b835e327f0f948ce37cc93187b3a33c",
    #     "https://signgo-bucket.s3.amazonaws.com/media/signbox/FilesNoFirmados/466432435317699/Carta_licencia.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA45XFJQA2SMB73TVY%2F20241208%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20241208T224010Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=f2f0925b9c9c880ac7567cbc8c04623baba82f23cb24e8954ebed9cf228621bc",
    # ]

    # # Lista de firmantes
    # firmantes = [
    #     {"name": "Jhonatan Galiano"},
    #     {"name": "Danny Marroquin"},
    #     {"name": "Josue Lopez"},
    #     {"name": "Hector Morales"},
    #     {"name": "Norman Sinay"},
    # ]

    # return render(request, 'prueba.html', {'pdf_files': pdf_files, 'firmantes': firmantes})

    # token = 'PZ63_x7nn2rLnxpAMbE94lN5k3iEwZscQFT0MtCk3sXzioGRUi4f4kVv3AYQcSntPtA'
    # find_licencia = LicenciasSistema.objects.get(TokenAuth=token)
    # print(find_licencia.pk)
    # find_renovaciones = RenovacionLicencia.objects.filter(licencia=find_licencia)
    # for i in find_renovaciones:
    #     print(i.fecha_renovacion)
    return render(request, 'helloworld.html')


@login_required
def home(request):
    try:
        # VALIDAR SI EL USUARIO ES INDIVIDUAL O DEPENDE DE EMPRESA
        find_type_license = PerfilSistema.objects.get(usuario=request.user.id)
        
        if find_type_license.empresa:
            find_licencias = LicenciasSistema.objects.filter(empresa=find_type_license.empresa.id)
        else:
            # USUARIO INDIVIDUAL
            find_usuario = UsuarioSistema.objects.get(UsuarioGeneral=request.user.pk)
            find_licencias = LicenciasSistema.objects.filter(usuario=find_usuario.pk)
        
        
        
        # SI NO EXISTEN LICENCIAS COMO EMPRESA NI INDIVIDUAL
        if not find_licencias:
            return render(request, 'home.html')
    
    except UsuarioSistema.DoesNotExist:
        return render(request, 'home.html')

    # Si existen licencias, pasar los datos al contexto y renderizar
    contexto = {
        'licencias': find_licencias
    }

    return render(request, 'home.html', contexto)


def salir(request):
    logout(request)
    return redirect('/home/')

@login_required
def administrar_usuarios(request):
    if not request.user.is_superuser:
        return render(request, 'AccesoDenegado.html')
    else:
        usuarios = PerfilSistema.objects.all()
        return render(request, 'users.html', {'users': usuarios})
    
@login_required
def crear_usuario(request):
    if not request.user.is_superuser:
        return render(request, 'AccesoDenegado.html')
    else:
        if request.method == 'POST': 
            nameUser = request.POST['nombreUsuario']
            empresaUser = request.POST['nombreEmpresa']
            emailUser = request.POST['email']
            psw1User = request.POST['psw1']
            psw2User = request.POST['psw2'] 
            nombres = request.POST['nombres']
            apellidos = request.POST['apellidos']
            cui = request.POST['cui']
            celular = request.POST['celular']         
        
            # Validación inicial: verificar si el usuario o el correo ya existen
            if User.objects.filter(username=nameUser).exists():
                messages.error(request, "El usuario ya existe en el sistema")
                return redirect('/users/crear/')
            elif User.objects.filter(email=emailUser).exists():
                messages.error(request, "El correo ya existe en el sistema")
                return redirect('/users/crear/')

            idEmpresa = None
            if 'isEmpresa' in request.POST:
                empresa_exists = EmpresaSistema.objects.filter(Nombre=empresaUser).exists()
                print(f'estado de busqueda de empresa: {empresa_exists}')
                if not empresa_exists:
                    messages.error(request, "La empresa ingresada no existe")
                    return redirect('/users/crear/')
                idEmpresa = EmpresaSistema.objects.get(Nombre=empresaUser)

            # Validación de contraseñas
            if psw1User != psw2User:
                messages.error(request, "Las contraseñas no coinciden")
                return redirect('/users/crear/')
            
            user = User.objects.create_user(username=nameUser, email=emailUser, password=psw1User, first_name=nombres, last_name=apellidos)
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
                'is_flujofirma': 'FlujoFirmaNormalAuth',
                'is_adminFlujoFirma': 'FlujoFirmaAdminAuth'
            }

            for key, group_name in grupos.items():
                group = Group.objects.get(name=group_name)
                if key in request.POST:
                    user.groups.add(group)
                
            user.save()

            userProfile = PerfilSistema(
                empresa=idEmpresa,
                usuario=user,
                Token=token
            )
            userProfile.save()
            
            detalleUsuario = UsuarioSistema(
                Nombres=nombres,
                Apellidos=apellidos, 
                Email=emailUser,
                Celular=celular,
                CUI=cui,
                Token=token,
                UsuarioGeneral=user
            )
            detalleUsuario.save()
            
            messages.success(request, "Usuario creado con éxito")
            return redirect('/users/')


        getEmpresas = EmpresaSistema.objects.all()
        listaEmpresas = []
        for empresa in getEmpresas:
            listaEmpresas.append(empresa.Nombre)

        return render(request, 'users_create.html', {'empresas': listaEmpresas})

@login_required
def editar_usuario(request, token_user):
    if not request.user.is_superuser:
        return render(request, 'AccesoDenegado.html')
    else:
        try:
            id_usuario = PerfilSistema.objects.get(Token=token_user)
            usuario = User.objects.get(id=id_usuario.usuario.id)
            usuario_sistema = UsuarioSistema.objects.get(UsuarioGeneral=id_usuario.usuario.id)
            if request.method == 'POST':
                username = request.POST['username']
                email = request.POST['email']
                password = request.POST['password']
                nombres = request.POST['nombres']
                apellidos = request.POST['apellidos']
                nombre_empresa = request.POST.get('nombreEmpresa', '').strip()
                is_superuser = request.POST.get('is_superuser') == 'on'
                
                empresa_editar = PerfilSistema.objects.get(usuario=id_usuario.usuario.id)
                
                # Validación para eliminar una empresa de usuario
                if not nombre_empresa:
                    if not empresa_editar.empresa == None:
                        empresa_editar.empresa = None
                        empresa_editar.save()
                    else:
                        None
                        
                else:
                    empresa_exists = EmpresaSistema.objects.filter(Nombre=nombre_empresa).exists()
                    if not empresa_exists:
                        messages.success(request, "Usuario editado con éxito")
                        return redirect('users')
                    idEmpresa = EmpresaSistema.objects.get(Nombre=nombre_empresa)
                    
                    empresa_editar.empresa = idEmpresa
                    empresa_editar.save()
                    
                
                if User.objects.filter(username=username).exists() and usuario.username != username:
                    messages.error(request, "El email ingresado ya existe")   
                    return redirect(f'/users/editar/{token_user}')
                else:
                    usuario.username = username
                
                if User.objects.filter(email=email).exists() and usuario.email != email:
                    messages.error(request, "El email ingresado ya existe")   
                    return redirect(f'/users/editar/{token_user}')
                else:
                    usuario.email = email
                    usuario_sistema.Email = email
                
                usuario.first_name = nombres
                usuario.last_name = apellidos
                
                usuario_sistema.Nombres = nombres
                usuario_sistema.Apellidos = apellidos
                    
                if password:
                    usuario.set_password(password)
            
                if 'is_superuser' in request.POST:
                    usuario.is_superuser = True
                else:
                    usuario.is_superuser = False
                    
                if 'is_active' in request.POST:
                    usuario.is_active = True
                else:
                    usuario.is_active = False

                
                # Validación de permisos por aplicación
                grupo_signbox = Group.objects.get(name='SignboxAuth')
                grupo_vol = Group.objects.get(name='VolAuth')
                grupo_oneshot = Group.objects.get(name='OneshotAuth')
                grupo_4identity = Group.objects.get(name='4identityAuth')
                grupo_esign = Group.objects.get(name='eSignAuth')
                grupo_signbol = Group.objects.get(name='SignbolAuth')

                grupo_plantilla = Group.objects.get(name='planillaAuth')
                grupo_signbolContactos = Group.objects.get(name='SignbolContactosAuth')
                grupo_signbolEnvios = Group.objects.get(name='SignbolEnviosAuth')
                grupo_signbolReportes = Group.objects.get(name='SignbolReportesAuth')
                grupo_signbolAdmin = Group.objects.get(name='SignbolAdminAuth')
                
                grupo_flujofirma_normal = Group.objects.get(name='FlujoFirmaNormalAuth')
                grupo_flujofirma_admin = Group.objects.get(name='FlujoFirmaAdminAuth')
                
                if 'is_signbox' in request.POST: usuario.groups.add(grupo_signbox)
                else: usuario.groups.remove(grupo_signbox)
                
                if 'is_oneshot' in request.POST: usuario.groups.add(grupo_oneshot)
                else: usuario.groups.remove(grupo_oneshot)
                
                if 'is_vol' in request.POST: usuario.groups.add(grupo_vol)
                else: usuario.groups.remove(grupo_vol)
                
                if 'is_4identity' in request.POST: usuario.groups.add(grupo_4identity)
                else: usuario.groups.remove(grupo_4identity)
                
                if 'is_esign' in request.POST: usuario.groups.add(grupo_esign)
                else: usuario.groups.remove(grupo_esign)
                
                if 'is_signbol' in request.POST: usuario.groups.add(grupo_signbol)
                else: usuario.groups.remove(grupo_signbol)
                
                if 'is_plantilla' in request.POST: usuario.groups.add(grupo_plantilla)
                else: usuario.groups.remove(grupo_plantilla)
                
                if 'is_contacto' in request.POST: usuario.groups.add(grupo_signbolContactos)
                else: usuario.groups.remove(grupo_signbolContactos)
                
                if 'is_envio' in request.POST: usuario.groups.add(grupo_signbolEnvios)
                else: usuario.groups.remove(grupo_signbolEnvios)
                
                if 'is_reportes' in request.POST: usuario.groups.add(grupo_signbolReportes)
                else: usuario.groups.remove(grupo_signbolReportes)
                
                if 'is_AdminSignbol' in request.POST: usuario.groups.add(grupo_signbolAdmin)
                else: usuario.groups.remove(grupo_signbolAdmin)
                
                if 'is_flujofirma' in request.POST: usuario.groups.add(grupo_flujofirma_normal)
                else: usuario.groups.remove(grupo_flujofirma_normal)
                
                if 'is_adminFlujoFirma' in request.POST: usuario.groups.add(grupo_flujofirma_admin)
                else: usuario.groups.remove(grupo_flujofirma_admin)
                
                messages.success(request, "Usuario editado con éxito")   
                usuario.save()
                usuario_sistema.save()
                return redirect('/users/')
        except Exception as e:
            messages.error(request, f'Error al editar el usuario: {e}')
            return redirect(f'/users/editar/{token_user}')
        
        try:
             
            miembroSignbox = usuario.groups.filter(name='SignboxAuth').exists()
            miembroVol = usuario.groups.filter(name='VolAuth').exists()
            miembroOneshot = usuario.groups.filter(name='OneshotAuth').exists()
            miembro4identity = usuario.groups.filter(name='4identityAuth').exists()
            miembroeSign = usuario.groups.filter(name='eSignAuth').exists()
            miembroSignbol = usuario.groups.filter(name='SignbolAuth').exists()
            
            miembroPlantilla = usuario.groups.filter(name='planillaAuth').exists()
            miembroSignbolContactos = usuario.groups.filter(name='SignbolContactosAuth').exists()
            miembroSignbolEnvios = usuario.groups.filter(name='SignbolEnviosAuth').exists()
            miembroSignbolReportes = usuario.groups.filter(name='SignbolReportesAuth').exists()
            miembroSignbolAdmin = usuario.groups.filter(name='SignbolAdminAuth').exists()
            
            miembroFlujoFirmaNormal = usuario.groups.filter(name='FlujoFirmaNormalAuth').exists()
            miembroFlujoFirmaAdmin = usuario.groups.filter(name='FlujoFirmaAdminAuth').exists()
            
            # Consultar si el usuario está asociado a empresa o tiene licencia individual
            find_user = UsuarioSistema.objects.get(Token=token_user)
            is_user_empresa = PerfilSistema.objects.get(usuario=find_user.UsuarioGeneral.id)

            # if LicenciasSistema.objects.filter(usuario=find_user.id): Linea anterior a modificación
            if LicenciasSistema.objects.filter(usuario=find_user.id).exists():
                LicenciasSistema.objects.filter(usuario=find_user.id)
                empresa_or_licencia = LicenciasSistema.objects.filter(usuario=find_user.id)
                tipo_licencia = 'licencia'
                print('tiene licencia')
            else:
                empresa_or_licencia = []
                tipo_licencia = 'None'
            
            if not is_user_empresa.empresa == None:
                find_empresa = PerfilSistema.objects.get(usuario=find_user.UsuarioGeneral)
                empresa_or_licencia = EmpresaSistema.objects.get(pk=find_empresa.empresa.id)
                tipo_licencia = 'empresa'
                
                
            find_user_context = UsuarioSistema.objects.get(UsuarioGeneral=usuario.pk)
            getEmpresas = EmpresaSistema.objects.all()
            listaEmpresas = []
            for empresa in getEmpresas:
                listaEmpresas.append(empresa.Nombre)
            
            contexto = {
                'empresas': listaEmpresas,
                'empresa_or_licencia': tipo_licencia,
                'asociado': empresa_or_licencia,
                'find_user_context': find_user_context, 
                'usuario': usuario,
                'usuario_editar': token_user,
                'miembroSignbox': miembroSignbox,
                'miembroVol': miembroVol,
                'miembroOneshot': miembroOneshot,
                'miembro4identity': miembro4identity,
                'miembroeSign': miembroeSign,
                'miembroSignbol': miembroSignbol,
                'miembroPlantilla': miembroPlantilla,
                'miembroSignbolContactos': miembroSignbolContactos,
                'miembroSignbolEnvios': miembroSignbolEnvios,
                'miembroSignbolReportes': miembroSignbolReportes,
                'miembroSignbolAdmin': miembroSignbolAdmin,
                'miembroFlujoFirmaNormal': miembroFlujoFirmaNormal,
                'miembroFlujoFirmaAdmin': miembroFlujoFirmaAdmin
            }

            return render(request, 'users_edit.html', contexto)
        except Exception as e:
            messages.error(request, f'Error al recuperar información del usuario: {e}')
            return redirect(f'/users/')

@login_required
def eliminar_usuario(request, usuario_id):
    if not request.user.is_superuser:
        return render(request, 'AccesoDenegado.html')
    else:
        usuario = User.objects.get(id=usuario_id)
        usuario.delete()
        return redirect('users')

@login_required
def adminBilling(request):
    if not request.user.is_superuser:
        return render(request, 'AccesoDenegado.html')
    else:
        if request.method == "GET":
            
            SignboxSandbox = billingSignboxSandbox.objects.get(id=1)
            SignboxProd = billingSignboxProd.objects.get(id=1)
            OneshotSandbox = billingOneshotSandbox.objects.get(id=1)
            OneshotProd = billingOneshotProd.objects.get(id=1)
            
            contexto = {
                'SignboxSandbox': SignboxSandbox,
                'SignboxProd': SignboxProd,
                'OneshotSandbox': OneshotSandbox,
                'OneshotProd': OneshotProd
            }
            
            return render(request, "adminBilling.html", contexto)
        else:
            UserProd = request.POST['userProd']
            PassProd = request.POST['passProd']
            UserSand = request.POST['userSandbox']
            PassSand = request.POST['passSandbox']
            Env = request.POST['selectCredentials']
            Credentials = request.POST['credentialsSelection']
            
            if Credentials == "oneshot":
                envSandbox = billingOneshotSandbox.objects.get(id=1)
                envProd = billingOneshotProd.objects.get(id=1)
                
                if Env == "0":
                    envSandbox.status = "1"
                    envProd.status = "0"
                else:
                    envProd.status = "1"
                    envSandbox.status = "0"
                
                envProd.user = UserProd
                envProd.password = PassProd    
                envSandbox.user = UserSand
                envSandbox.password = PassSand
                envSandbox.save()
                envProd.save()           
            else:
                envSandbox = billingSignboxSandbox.objects.get(id=1)
                envProd = billingSignboxProd.objects.get(id=1)
                if Env == "0":
                    envSandbox.status = "1"
                    envProd.status = "0"
                else:
                    envProd.status = "1"
                    envSandbox.status = "0"
                
                envProd.user = UserProd
                envProd.password = PassProd
                envSandbox.user = UserSand
                envSandbox.password = PassSand
                envSandbox.save()
                envProd.save()
        
            return redirect("billing")

@login_required     
def hostIP(request):
    if not request.user.is_superuser:
        return render(request, 'AccesoDenegado.html')
    else:
        if not oneshotAPI.objects.exists():
            nuevoRegistro = oneshotAPI(ip="192.168.11.16:8080", protocol="0")
            nuevoRegistro.save()
        
        if not signboxAPI.objects.exists():
            nuevoRegistro = signboxAPI(ip="192.168.11.17:8080", protocol="0")
            nuevoRegistro.save()
            
        if not volIP.objects.exists():
            nuevoRegistro = volIP(ip="192.168.11.18:8080", protocol="0")
            nuevoRegistro.save()
            
        if not webhookIP.objects.exists():
            nuevoRegistro = webhookIP(ip="192.168.11.18:8080", protocol="0")
            nuevoRegistro.save()
            
        dataOneshot = oneshotAPI.objects.get(id=1)
        dataSignbox = signboxAPI.objects.get(id=1)
        dataVol = volIP.objects.get(id=1)
        dataWebhook = webhookIP.objects.get(id=1)
        
        
            
        if request.method == "POST":
            
            selectSignbox = request.POST['sigbboxSelect']
            inputSignbox = request.POST['signboxInput']
            selectOneshot = request.POST['oneshotSelect']
            inputOneshot = request.POST['oneshotInput']
            selectVol = request.POST['volSelect']
            inputVol = request.POST['volInput']
            selectWebhook = request.POST['webhookSelect']
            inputWebhook = request.POST['webhookInput']
            
            
            dataOneshot.ip = inputOneshot
            dataOneshot.protocol = selectOneshot
            
            dataSignbox.ip = inputSignbox
            dataSignbox.protocol = selectSignbox
            
            dataVol.ip = inputVol
            dataVol.protocol = selectVol 
            
            dataWebhook.ip = inputWebhook
            dataWebhook.protocol = selectWebhook
            
            dataOneshot.save()
            dataSignbox.save()
            dataVol.save()  
            dataWebhook.save()   
            
            if not token_oneshot.objects.exists():
                save_token = token_oneshot(
                    token = request.POST['token_value']
                )
                save_token.save()
            else: 
                find_token = token_oneshot.objects.filter().first()
                find_token.token = request.POST['token_value']
                find_token.save()
            
            
            messages.success(request, 'Cambios guardados con éxito')
            return redirect('hostIP')
        
        find_token = token_oneshot.objects.filter().first()
                
        contexto = {
            'OneshotIP': dataOneshot,
            'SignboxIP': dataSignbox,
            'VolIP': dataVol,
            'dataWebhook': dataWebhook,
            'token_oneshot': find_token
        }    
            
        return render(request, "hostAPI.html", contexto)
    
def validate_tokens_api_oneshot(request):
    
    if request.method == "POST":
        protocolo, ip = validar_API_oneshot()
        url_API = f'{protocolo}://{ip}/api/v1/tokens'
            
        payload = {}
        headers = {}
            
        try:
            response = requests.request("GET", url_API, headers=headers, data=payload)
            response_parse = json.loads(response.text)
            if response_parse['status'] == '200 OK':
                return JsonResponse({'success': True, 'data': json.dumps(response_parse['details'])}, status=200)
            else:         
                messages.error(request, f'Error al consultar tokens')
                return JsonResponse({"success": False, "error": 'No se ha encontrado el API'}) 
        
        except Exception as e:
            messages.error(request, f'Error al consultar tokens: {e}')
            return JsonResponse({"success": False, "error": "error"})
            
    else:
        return JsonResponse({"success": False, "error": "Esta URL no acepta solicitudes"})
    
def crear_token(request):
    if request.method == 'POST':
        
        username = request.POST['username_value']
        password = request.POST['psw_value']
        pin = request.POST['pin_value']
        env = request.POST['env_value']
        
        protocolo, ip = validar_API_oneshot()
        url = f'{protocolo}://{ip}/api/v1/token'
        

        payload = json.dumps({
            "username": username,
            "password": password,
            "pin": pin,
            "env": env
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response_parse = json.loads(response.text)
        
        if response_parse['status'] == '200 OK':
            messages.success(request, f'Token Creado con Éxito: {response_parse["details"]}')
        elif response_parse['status'] == '400 Bad Request':
            messages.error(request, f'Error: Faltan parámetros requeridos: {response_parse["details"]}')
        elif response_parse['status'] == '404 Not Found':
            messages.error(request, f'Error: No se ha encontrado el id de la RAOs. Asegurese de que las credenciales son correctas: {response_parse["details"]}')
        else:
            messages.error(request, f'Error Desconocido: {response_parse["details"]}')
            
        
        return redirect('/hostIP/')    
    return redirect('/hostIP/')
    
    
def accesoDenegado(request):
    return render(request, 'AccesoDenegado.html')


def password_reset(request: HttpRequest):
    if request.method == 'POST':
        try:
            correo_usuario = request.POST['username']
            validar_correo = User.objects.filter(username=correo_usuario).exists()
            if validar_correo:
                id_usuario = User.objects.get(username=correo_usuario)
                scheme = request.scheme
                host = request.get_host()
                url = f'{scheme}://{host}'
                send_mail_resetPassword = password_reset_mail(id_usuario.pk, url)
                if send_mail_resetPassword:
                    messages.success(request, 'Se ha enviado un correo con las instrucciones para cambiar su contraseña.')
                    return redirect(reverse('password_reset'))
                else:
                    messages.error(request, 'Error: No se ha podido enviar el correo electrónico')
                    return redirect(reverse('password_reset'))
            else:
                messages.error(request, 'No se han encontrado coincidencias con el correo proporcionado.')
                return redirect(reverse('password_reset'))
        except Exception as e:
            print(f'Error password_reset: {e}')
            messages.error(request, f'Error: {e}')
            return redirect(reverse('password_reset'))
    return render(request, 'registration/password_reset.html')

def password_reset_mail(id_send, url):
    try:
        id_usuario = User.objects.get(id=id_send)
        uidb64 = urlsafe_base64_encode(force_bytes(id_usuario.pk))
        user = get_user_model().objects.get(username=id_usuario.username)
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)     
        url = f'{url}/accounts/reset/{uidb64}/{token}'
        correo_electronico = id_usuario.username
        remitente = 'notificaciones@signgo.com.gt'
        destinatario = correo_electronico
        asunto = "Solicitud para Reestablecer Contraseña"
        
        context = {
            'data': url,
            'nombre': id_usuario.username,
            'asunto': asunto
        }
            
        template_html = render_to_string('registration/password_mail.html', context)
            
        try:
            send_mail(
                asunto,
                '',
                remitente,
                [destinatario],
                fail_silently=False,
                html_message=template_html
            )
            print("Correo Enviado")
            return True
        except Exception as e:
            print(f"Error al enviar el correo: {e}")
            return False
    except Exception as e:
        print(f'Error password_reset_mail: {e}')
        return False
    
def password_reset_change(request, uidb64, token):
    try:
        uid = uidb64
        token = token
        uid = urlsafe_base64_decode(uid).decode('utf-8')
        user = get_user_model().objects.get(pk=uid)
        token_generator = PasswordResetTokenGenerator()
        is_valid = token_generator.check_token(user, token)
        if is_valid:
            if request.method == 'POST':
                password1 = request.POST['password1']
                password2 = request.POST['password2']
                if password1 == password2: 
                    usuario = User.objects.get(id=uid)
                    usuario.set_password(password1)
                    usuario.save()
                    messages.success(request, 'Contraseña cambiada con éxito.')
                    return redirect('/home/')    
                else: 
                    messages.error(request, 'Las contraseñas no coinciden, intentelo nuevamente.')
                    return redirect(f'/accounts/reset/{uidb64}/{token}')
            return render(request, 'registration/password_change.html')
        else:
            return render(request, '404.html')
    except Exception as e:
        print(f'Error password_reset_change: {e}')
        return render(request, '404.html')
    
def administrar_empresas(request):
    try:
        if request.method == 'POST':
            # Filtros de busqueda 
            nombre_empresa = request.POST.get('nombreEmpresa')
            nit = request.POST.get('nit')
            ciudad = request.POST.get('ciudad')
            fecha_desde = request.POST.get('fechaRegistroDesde')
            fecha_hasta = request.POST.get('fechaRegistroHasta')
            estado = request.POST.get('estado')
            
            resultados = EmpresaSistema.objects.all()
            
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
            return render(request, 'empresas.html', contexto)
        else: 
            resultados = EmpresaSistema.objects.all().order_by('-id')[:50]
            contexto = {
                'Empresas': resultados
            }
            return render(request, 'empresas.html', contexto)
    except Exception as e:
        messages.error(request, "Error al cargar empresas")
        return redirect(reverse('administrar_empresas'))


def crear_empresa(request):
    if request.method == 'POST':
        NombreEmpresa = request.POST['nombreEmpresa']
        NitEmpresa = request.POST['nit']
        SectorEmpresa = request.POST['sector']
        NumeroContacto = request.POST['numero_contacto']
        EmailContacto = request.POST['email_ontacto']
        NombreContacto = request.POST['nombre_contacto']
        TokenAuthEmpresa = secrets.token_urlsafe(30)
        
        InsertEmpresa = EmpresaSistema(
            Nombre = NombreEmpresa,
            NIT = NitEmpresa,
            Sector = SectorEmpresa,
            Token = TokenAuthEmpresa,
            NumeroContacto = NumeroContacto,
            EmailContacto = EmailContacto,
            NombreContacto = NombreContacto
        )
        InsertEmpresa.save()
        return redirect('/planilla/crearEmpresa/')
    return render(request, 'empresas_create.html')

def editar_empresa(request, token_emp):
    if not request.user.is_superuser:
        return render(request, 'AccesoDenegado.html')
    else:
        try:
            if request.method == 'POST':
                empresa_edit = EmpresaSistema.objects.get(Token=token_emp)
                empresa_edit.Nombre = request.POST['nombre_empresa']
                empresa_edit.NIT = request.POST['nit_empresa']
                empresa_edit.Sector = request.POST['sector_empresa']
                empresa_edit.NumeroContacto = request.POST['numero_contacto']
                empresa_edit.EmailContacto = request.POST['email_contacto']
                empresa_edit.NombreContacto = request.POST['nombre_contacto']
                empresa_edit.save()
                return redirect(f'/empresas')
            else:
                try:
                    find_empresa = EmpresaSistema.objects.get(Token=token_emp)
                    find_users = PerfilSistema.objects.filter(empresa_id=find_empresa.pk)
                    find_licencias = LicenciasSistema.objects.filter(empresa=find_empresa.pk)
                except ObjectDoesNotExist:
                    return render(request, 'AccesoDenegado.html')
                
                contexto = {
                    'empresa_editar': token_emp,
                    'empresa': find_empresa,
                    'Usuarios': find_users,
                    'Licencias': find_licencias
                }
                return render(request, 'empresas_edit.html', contexto)
            
        except Exception as e:
            messages.error(request, f'Error al editar empresa: {e}') 
            return redirect(f'/empresas/editar/{token_emp}')
        
        
def licencias(request):
    if not request.user.is_superuser:
        return render(request, 'AccesoDenegado.html')
    else:
        licencias = LicenciasSistema.objects.all()
        contexto = {
            'Licencias': licencias
        }
    return render(request, 'licencias.html', contexto)

def licencias_crear(request):
    if not request.user.is_superuser:
        return render(request, 'AccesoDenegado.html')
    else:
        if request.method == 'POST':
            empresa_usuario = request.POST.get('empresaUsuario', '').strip()
            fecha_emision = request.POST.get('fechaEmision')
            fecha_vencimiento = request.POST.get('fechaVencimiento')
            tipo_licencia = request.POST.get('tipoLicencia')
            estado_licencia = request.POST.get('estadoLicencia')  
            modalidad_licencia = request.POST.get('modalidadLicencia')  
            cantidad_creditos = request.POST.get('cantidadCreditos')
            precio = request.POST.get('precio')
            precio_creditos = request.POST.get('precio_creditos')
            usuario_billing = request.POST.get('usuarioBilling')  
            contrasena_billing = request.POST.get('contrasenaBilling') 
            observaciones = request.POST.get('observaciones') 
            env_trabajo = request.POST.get('env')
                
            
            
            # Dividir entre empresa y usuario
            empresa = None
            usuario = None
            if empresa_usuario:
                empresa = EmpresaSistema.objects.filter(Nombre=empresa_usuario).first()
                if not empresa:  # Si no es empresa, buscar como usuario
                    usuario = UsuarioSistema.objects.get(Email=empresa_usuario)

            if not empresa and not usuario:
                messages.error(request, "Debe asociar la licencia a una empresa o un usuario válido.")
                return redirect('/licencias/crear')  # Cambiar por el nombre de tu URL correspondiente

            Token = secrets.token_urlsafe(50)
            
            # Crear la licencia
            try:
                licencia = LicenciasSistema(
                    empresa=empresa,
                    usuario=usuario,
                    tipo=tipo_licencia,
                    cantidad_creditos=cantidad_creditos,
                    acumulado_creditos=cantidad_creditos,
                    costo_tipo=precio,
                    costo_creditos=precio_creditos,
                    fecha_inicio=fecha_emision,
                    fecha_fin=fecha_vencimiento,
                    activa="Activa",
                    usuario_billing=usuario_billing,
                    contrasena_billing=contrasena_billing,
                    observaciones=observaciones,
                    modalidad=modalidad_licencia,
                    TokenAuth=Token,
                    env=env_trabajo
                )
                licencia.full_clean()  # Validar el modelo
                licencia.save()
                messages.success(request, "Licencia creada con éxito.")
                return redirect('/licencias') 
            except ValidationError as e:
                messages.error(request, f"Error al crear la licencia: {e}")
            
            return redirect('/licencias/crear')  # Cambiar por el nombre de tu URL correspondiente
        else: 
            empresas_usuarios = EmpresaSistema.objects.all()
            lista_empresas_usuarios = []
            for empresa in empresas_usuarios:
                lista_empresas_usuarios.append(empresa.Nombre)
            
            contexto = {
                'empresasUsuarios': lista_empresas_usuarios
            }
            return render(request, 'licencias_create.html', contexto)

def licencias_editar(request, token_lc):
    if not request.user.is_superuser:
        return render(request, 'AccesoDenegado.html')
    else:
        try:
            if request.method == 'POST':
                find_licencia = LicenciasSistema.objects.get(TokenAuth=token_lc)
                
                fecha_emision = request.POST.get('fecha_inicio')
                fecha_vencimiento = request.POST.get('fecha_fin')
                tipo_licencia = request.POST.get('tipo')
                estado_licencia = request.POST.get('estado')  
                modalidad_licencia = request.POST.get('modalidad') 
                cantidad_creditos = request.POST.get('cantidad_creditos')
                precio_tipo_licencia = request.POST.get('costo_tipo', '').strip() 
                precio_creditos = request.POST.get('costo_creditos', '').strip()
                
                find_licencia = LicenciasSistema.objects.get(TokenAuth=token_lc)
                find_licencia.fecha_inicio = fecha_emision
                find_licencia.fecha_fin = fecha_vencimiento
                find_licencia.tipo = tipo_licencia
                find_licencia.activa = estado_licencia
                find_licencia.modalidad = modalidad_licencia
                find_licencia.acumulado_creditos = (find_licencia.acumulado_creditos - find_licencia.cantidad_creditos) + int(cantidad_creditos)
                find_licencia.cantidad_creditos = int(cantidad_creditos)
                find_licencia.env = request.POST.get('env_licencia')
                find_licencia.usuario_billing = request.POST.get('usuario_billing')
                find_licencia.contrasena_billing = request.POST.get('contraseña_billint')
                
                
                if precio_tipo_licencia:
                    find_licencia.costo_tipo = precio_tipo_licencia
                
                if precio_creditos:
                    find_licencia.costo_creditos = precio_creditos
                
                find_licencia.save()

                messages.success(request, 'Cambios guardados con éxito')
                return redirect(f'/licencias/editar/{token_lc}')
            else:
                try:
                    find_licencia = LicenciasSistema.objects.get(TokenAuth=token_lc)
                except ObjectDoesNotExist:
                    return render(request, 'AccesoDenegado.html')
                
                if find_licencia.usuario:
                    relacion_usuario = UsuarioSistema.objects.get(id=find_licencia.usuario.id)
                    empresa_or_user = "user"
                else:
                    relacion_usuario = EmpresaSistema.objects.get(id=find_licencia.empresa.id)
                    empresa_or_user = "empresa"
                    
                find_renovaciones = RenovacionLicencia.objects.filter(licencia=find_licencia)
                find_compras_extra = CompraExtraordinaria.objects.filter(licencia=find_licencia)
                                
                contexto = {
                        'licencia': find_licencia,
                        'relacion': relacion_usuario,
                        'empresa_or_user': empresa_or_user,
                        'token_lc': token_lc,
                        'token_rlc': token_lc,
                        'renovaciones': find_renovaciones,
                        'find_compras_extra': find_compras_extra
                    }
                
                return render(request, 'licencias_editar.html', contexto)
        except Exception as e:
            messages.error(request, f'Error al editar licencia: {e}')
            return redirect(f'/licencias/editar/{token_lc}')
            
    

def licencias_renovar(request, token_rlc):
    if request.method == 'POST':
        try:
            new_fecha_inicio = request.POST.get('new_fecha_inicio')
            new_fecha_fin = request.POST.get('new_fecha_fin')
            new_cantidad_creditos = request.POST.get('new_cantidad_creditos')
            new_costo_creditos = request.POST.get('new_costo_creditos')
            new_precio_licencia = request.POST.get('new_costo_licencia')
            id_licencia = request.POST.get('id_licencia')
            
            find_renovacion = LicenciasSistema.objects.get(TokenAuth=token_rlc)
            token_renovacion = secrets.token_urlsafe(50)
            
            renovar_licencia = RenovacionLicencia(
                licencia = find_renovacion,
                fecha_anterior_emision = find_renovacion.fecha_inicio,
                fecha_anterior_fin = find_renovacion.fecha_fin,
                nueva_fecha_emisión = new_fecha_inicio,
                nueva_fecha_fin = new_fecha_fin,
                costo_renovacion_licencia = new_precio_licencia,
                costo_renovacion_creditos = new_costo_creditos,
                cantidad_creditos = new_cantidad_creditos,
                Token = token_renovacion
            )
            renovar_licencia.save()
            
            messages.success(request, f'Licencia renovada con éxito')
            return redirect(f'/licencias/editar/{token_rlc}')
        except Exception as e:
            messages.error(request, f'Error al renovar licencia: {e}')
            return redirect(f'/licencias/editar/{token_rlc}')
        

def compra_extra(request, token_lc):
    if request.method == 'POST':
        try:
            print(token_lc)
            find_licencia = LicenciasSistema.objects.get(TokenAuth=token_lc)
            
            cantidad_creditos_request = request.POST.get('extra_cantidad_creditos')
            precio_creditos_request = request.POST.get('extra_precio_creditos')
            
            save_compra = CompraExtraordinaria(
                cantidad_creditos = int(cantidad_creditos_request),
                precio_creditos = float(precio_creditos_request),
                licencia = find_licencia
            )
            save_compra.save()
            
            find_licencia.acumulado_creditos = find_licencia.acumulado_creditos + int(cantidad_creditos_request)
            find_licencia.save()
            
            messages.success(request, "Compra Extraordinaria Agregada con Éxito")
            return redirect(f'/licencias/editar/{token_lc}')
        except Exception as e:
            print(e)
            messages.error(request, f"{e}")
            return redirect(f'/licencias')
    else:
        return HttpResponse("Esta URL no acepta solicitudes")
    
def validar_API_oneshot():
    
    dataOneshot = oneshotAPI.objects.get(id=1)
    protocol = "http" if dataOneshot.protocol == "0" else "https"
    ip = dataOneshot.ip    
    
    return protocol, ip
        
        




    



