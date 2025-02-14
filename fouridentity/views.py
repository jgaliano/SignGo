from django.shortcuts import render
import os
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import zipfile
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
import json
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

def validatePermissions(user):
    return user.groups.filter(name='4identityAuth').exists()

# Create your views here.
@login_required
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
def helloworld(request):
    return render(request, 'fouridentity/helloworld.html')

@login_required
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
def home_4identity(request):
    if request.method == "GET":
        return render(request, 'fouridentity/4identity_home.html')
    else:
        nombre_archivos = []
        pdf_files = request.FILES.getlist('pdf_files')
        destino_carpeta = os.path.join(settings.MEDIA_ROOT, '4identity/4identity_files/')
        
        for pdf_file in pdf_files:
            nombre_inicial = pdf_file.name
            nombre_archivos.append(nombre_inicial)
            destino_archivo_nuevo = os.path.join(destino_carpeta, nombre_inicial)
            
            with open(destino_archivo_nuevo, 'wb') as archivo_destino:
                for parte in pdf_file.chunks():
                    archivo_destino.write(parte)
                    
        archivos4 = {
            'nameArchivos': nombre_archivos
        }
        
        request.session['files4'] = archivos4

        return HttpResponseRedirect('/4identity/sign_4identity/')
    
@csrf_exempt
def handle_uploaded_file(uploaded_file, document_id):
    if not uploaded_file:
        return False, None

    try:
        # Define la ruta donde se guardará el archivo
        upload_dir = './media/4identity/4identity_prezip/'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Procesa el nombre del archivo
        file_name = uploaded_file.name
        file_name = ''.join(c if c.isalnum() or c in ['.', '_', '-'] else '_' for c in file_name)
        file_name, extension = os.path.splitext(file_name)
        file_name = f"{document_id}{extension}"

        # Guarda el archivo en la ruta especificada
        with open(os.path.join(upload_dir, file_name), 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        return True, file_name
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")
        return False, None

@login_required
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
@csrf_exempt    
def upload_file(request):
    if request.method == "GET":
        info_sessin = request.session.get('files4', {})
        lista_archivos4 = info_sessin.get('nameArchivos')
        
        info_document = []
        x = 0
        for nombre in lista_archivos4:
            x+= 1
            info_document.append([x, nombre, '310KB'])

        encriptar = zipFiles(lista_archivos4)
        print(encriptar)
        
        nameArchivos = "Documentos_sign.zip"
        nameIdFiles = "Documentos_sign"
        ruta_files = './media/4identity/4identity_zip/' + nameArchivos
        
        data_info = {
            'resultados': info_document,
            'folder': '',
            'url': ruta_files,
            'documentName': nameArchivos,
            'documentID': nameIdFiles,
            'tipo': 'PAdES',
            'url_4identity_server_sign': '/media/bit4id-sign.js'
        }  

        return render(request, 'fouridentity/4identity_sign.html', data_info)
    
    elif request.method == 'POST' and request.FILES['attach']:
        uploaded_file = request.FILES['attach']
        document_id = request.POST.get('documentID', '')
        
        success, file_name = handle_uploaded_file(uploaded_file, document_id)
        name_archivo = document_id + '.zip'
        
        

        if success:
            # Unziparchivos = información de base de datos no relacional en archivo .json
            unziparchivos = unzipFiles(name_archivo)
            print(unziparchivos)
            
            datosjson = {
                'nombres': unziparchivos
            }
            
            ruta_archivo = './media/4identity/data4identity.json'
            with open(ruta_archivo, 'w') as archivo:
                json.dump(datosjson, archivo)
            
            return HttpResponseRedirect('/4identity/done_4identity/')
        else:
            return HttpResponseRedirect('/4identity/sign-end-error/')
    else:
        return HttpResponseRedirect('/4identity/sign-end-error/')
    
def zipFiles(listaFiles):
    ruta_zip = './media/4identity/4identity_zip/Documentos_sign.zip'
    
    with zipfile.ZipFile(ruta_zip, 'w') as zipf:
        for archivo in listaFiles:
            zipf.write('./media/4identity/4identity_files/' + archivo, archivo)
                  
    return "listo"

@login_required
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
@csrf_exempt
def sign_end_ok(request):
    return render(request, '4identity/sign_ok.html')

@login_required
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
@csrf_exempt
def sign_end_error(request):
    return HttpResponse("Error en el proceso de firmado, valide el flujo")

def unzipFiles(nameArchivo):
    ruta_zip_subido = default_storage.path('4identity/4identity_prezip/' + nameArchivo)
    directorio_destino = './media/4identity/4identity_sign/'
    
    with zipfile.ZipFile(ruta_zip_subido, 'r') as zip_ref:
        zip_ref.extractall(directorio_destino)
        nombres_archivos_extraidos = zip_ref.namelist()
    return nombres_archivos_extraidos

@login_required
@user_passes_test(validatePermissions, login_url='/acceso-denegado/')
def done_4identity(request):
    contenido = []       
    print(contenido)
    info_document = []
    
    ruta_archivo = './media/4identity/data4identity.json'
    with open(ruta_archivo, 'r') as archivo:
        datos_json = json.load(archivo)
        print(datos_json)
        
    data_Document = datos_json['nombres']
    
    x = 0
    for nombre in data_Document:
        x+= 1
        info_document.append([x, nombre, '310KB'])
    
    data_info = {
            'resultados': info_document,
    }

    return render(request, 'fouridentity/4identity_done.html', data_info)