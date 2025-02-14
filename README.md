![image](https://github.com/galianoccg/Sistema_DemoFirma/assets/125469477/73150046-472f-4016-a5c7-1144aacc368f)

Sistema desarrollado para integrar dentro de una misma aplicación web las 3 API de UANATACA

-----------
ONESHOT
-----------
Pasos Firma:

- VideoId Request
- Realizar Video Id
- Validate Request
- Approve Request
- Cargar documentos
- Enviar correo con documentos
- Generar OTP
- Firmar

--------------------------------------------
ERRORES DOCUMENTADOS DE LA RESPUESTA DEL API
--------------------------------------------
{"result": true, "error": null} = no hay errores

{"result": null, "error": {"msg": "Pin invalid", "code": 403, "error_code": 3, "details": ""}} = PIN invalido

{"result": null, "error": {"msg": "Invalid credentials", "code": 401, "error_code": 1, "details": ""}} = Contraseña incorrecta

{"result": null, "error": {"msg": "Token not found", "code": 403, "error_code": 2, "details": ""}} = Token incorrecto


-----------
SIGNBOX
----------
git restore --staged media/4identity/4identity_files/*
git restore --staged media/vol/Reportes/
git restore --staged media/vol/FilesValidar/
git restore --staged media/signbox/FilesFirmados/
git restore --staged media/signbox/FilesNoFirmados/
git restore --staged media/oneshot/FilesNoFirmados/
git restore --staged media/oneshot/FilesFirmados/
git restore --staged media/4identity/4identity_prezip/
git restore --staged media/4identity/4identity_sign/
git restore --staged media/4identity/4identity_zip/
git restore --staged media/oneshot/Video/VideoIdentificaciones/




Versiones de dependencias: 
xhtml2pdf==0.2.8
reportlab==3.6.12











    <!-- MESSAGES -->
        {% if messages %}
            <div class="toast-container position-fixed top-0 end-0 p-3">
                {% for message in messages %}
                    <div id="liveToast" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                        <div class="toast-header" style="color: white; background-color:{% if 'danger' in message.tags %}red{% elif 'success' in message.tags %}green{% elif 'warning' in message.tags %}orange{% else %}red{% endif %}">
                            <strong class="me-auto">{% if 'danger' in message.tags %}Error{% endif %}</strong>
                            <small></small>
                            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                        </div>
                        <div class="toast-body">
                            {{ message }}
                        </div>
                    </div>
                {% endfor %}
            </div>
              

            <script>
                document.addEventListener('DOMContentLoaded', function () {
                    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
                    const toastList = toastElList.map(function (toastEl) {
                        return new bootstrap.Toast(toastEl);
                    });
                    toastList.forEach(toast => toast.show());
                });
            </script>      
        {% endif %}
    <!-- MESSAGES -->



192.168.10.11:8086



    <!-- OVERLAY -->
        <div id="overlay" class="d-none position-fixed w-100 h-100 top-0 start-0 bg-dark bg-opacity-75" style="z-index: 1050;">
            <div class="d-flex flex-column justify-content-center align-items-center h-100">
                <div class="spinner-border text-light" role="status" style="width: 3rem; height: 3rem;"></div>
                <span class="mt-2 text-light">CARGANDO...</span>
            </div>
        </div>
    <!-- OVERLAY -->



        /* OVERLAY */
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }

        .spinner-border {
            width: 3rem;
            height: 3rem;
            color: #ffffff;
        }
        /* OVERLAY */


                // OVERLAY
        document.addEventListener("DOMContentLoaded", () => {
            if (sessionStorage.getItem("showOverlay") === "true") {
                document.getElementById("overlay").classList.add("d-none"); // Oculta el overlay
                sessionStorage.removeItem("showOverlay"); // Limpia el estado
            }
        });

        document.querySelectorAll(".validateButton").forEach(button => {
            button.addEventListener("click", function() {
                document.getElementById("overlay").classList.remove("d-none"); // Mostrar overlay
                sessionStorage.setItem("showOverlay", "true"); // Guardar estado en sessionStorage
            });
        });
        // OVERLAY


        




        
        
        
        
        // HIDE MODAL
        var miModal = document.getElementById('exampleModal1')
        miModal.style.display = "None"
                    
        // SHOW SPINNER
        document.getElementById("overlay").classList.remove("d-none"); // Mostrar overlay
        sessionStorage.setItem("showOverlay", "true"); // Guardar estado en sessionStorage













REGLAS FLUJO FIRMA:
- A cada documento solo se le puede agregar la firma de una persona 1 vez
- Si se agregan más solo se tomara en cuenta la primera que se colocó
- Lo ideal sería que solo se puedan poner 1 vez




[
    {'firmante_id': '1', 'page': 1, 'x': 10.800048828125, 'y': 981.5875244140625},      = Superior Izquierdo
    {'firmante_id': '2', 'page': 1, 'x': 510.33758544921875, 'y': 981.5875244140625},   = Superior Derecho
    {'firmante_id': '3', 'page': 1, 'x': 10.800048828125, 'y': 109.20001220703125},     = Inferior Izquierdo
    {'firmante_id': '4', 'page': 1, 'x': 510.33758544921875, 'y': 109.20001220703125}   = Inferior Derecho
]



Si la licencia está inactiva le permite acceder a la vista de creación de flujo pero ahí termina el proceso si la licencia está vencida o si no tiene licencia.


[
    {
        'firmante_id': '28', 'document_url': 'https://signgo-bucket.s3.amazonaws.com/media/flujofirma/FilesNoFirmados/605157441088810/prueba_varias_paginas.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA45XFJQA2SMB73TVY%2F20241223%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20241223T150903Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=b8c33be86bb61bf4cea04648f3faccd27c568882bd43bbcb468b469f63be5679', 'document_name': 'prueba_varias_paginas.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA45XFJQA2SMB73TVY%2F20241223%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20241223T150903Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=b8c33be86bb61bf4cea04648f3faccd27c568882bd43bbcb468b469f63be5679', 'page': 2, 'x': 426.93756103515625, 'y': 292.1624755859375}, 

    {
        'firmante_id': '28', 'document_url': 'https://signgo-bucket.s3.amazonaws.com/media/flujofirma/FilesNoFirmados/605157441088810/Prueba_2.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA45XFJQA2SMB73TVY%2F20241223%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20241223T150903Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=0c018ed03992fa9bd7967571bb40e4825c4314cfb2e2e3180c022be283532d6a', 'document_name': 'Prueba_2.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA45XFJQA2SMB73TVY%2F20241223%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20241223T150903Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=0c018ed03992fa9bd7967571bb40e4825c4314cfb2e2e3180c022be283532d6a', 'page': 1, 'x': 191.9375, 'y': 648.1875610351562
    }
]


80,620,250,670		215,620,385,670		380,620,550,670
10,981			260,981			510,981	


80,140,250,190		215,140,385,190		380,140,550,190
10,109			260,109			510,109






Superior original:
x=80, y=620			x=215,y=620			x=380,y=620
Inferior obtenido:
x=10, y=981			x=260,y=981			x=510,y=981	

Inferior requerido:
x=80,y=140			x=215,y=140			x=380,y=140
Inferior obtenido:
x=10,y=109			x=260,y=109			x=510,y=109


x_obtenidos = [10, 260, 510]
y_obtenidos = [109, 109, 109]

x_requeridos = [convertir_x(x) for x in x_obtenidos]
y_requeridos = [convertir_y(y) for y in y_obtenidos]


Inferior obtenido:
x=10, y=981			x=510,y=981	
Superior requerido:
x=10, y=730			x=430,y=730


Inferior obtenido:
x=10,y=109			x=510,y=109
Inferior requerido:
x=10,y=10			x=430,y=10			



x_obtenidos = [10, 260, 510]
y_obtenidos = [109, 109, 109]

x_requeridos = [convertir_x(x) for x in x_obtenidos]
y_requeridos = [convertir_y(y) for y in y_obtenidos]

10,10,180,60
430,10,600,60
x=170
y=50



ONESHOT
-------

https://d9c4-190-242-146-70.ngrok-free.app
{
    "status": "200 OK",
    "details": {
        "videoid_pk": 12818,
        "videoid_link": "https://www.sandbox.uanataca.com/lcmpl/videoid/ZjIxYTQyMjdlZWEwNDA5NzgyYWY4YzJjNjk2MmEwNDU6eklwOURFdDN2VllKendFV2gxbmowT3l0ejBWaUwwZDhfbnA5ZmFYdXB2cE5DbmNpT21sM3pVdHAwN2h5YndYajdxVWxsMkZaT2NJLWdFUlR5ZThpTW9Ra3ZPVG5FYjBEcTFFcWpoZXFpT1U9OjM4MjI1NWE5LWY2ZDQtNDhlOS04NjhkLTUyZDcyOTNmNzViNg==?customer=ccg",
        "request_pk": 447562
    }
}

{
    "status": "VIDEOINCOMPLETE", 
    "date": "2021-07-20T08:08:21.132394", 
    "previous_status": "VIDEOPENDING", 
    "request": 46760, 
    "registration_authority": 139
}

https://lima.sandbox.uanataca.com/api/v1/videoid/12819/download/video"
{{proto}}://{{host}}/api/v1/videoid/9977/download/video

VIDEOPENDING
VIDEOINCOMPLETE
VIDEOERROR
PENDIENTE



https://lima.sandbox.uanataca.com/video/f297bff9-93b9-40ab-887a-0ae38c9e9fe1



"webhook_url": "https://d9c4-190-242-146-70.ngrok-free.app"




aws bucket politica anterior:
{
    "Version": "2012-10-17",
    "Id": "Policy1732895737090",
    "Statement": [
        {
            "Sid": "Stmt1732895704319",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::signgo-bucket/*"
        }
    ]
}




si no se ha enviado ninguno, entonces enviar






{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::signgo-bucket/*",
            "Condition": {
                "StringLike": {
                    "aws:Referer": [
                        "http://signgo.com.gt/*",
                        "https://signgo.com.gt/*"
                    ]
                },
                "IpAddress": {
                    "aws:SourceIp": "13.58.166.143/32"
                }
            }
        }
    ]
}





######################################################
ENVIO DE VARIOS DOCUMENTOS EN ONESHOT
¿Se envían varios documento en el mismo request de 'upload document' y el id de la respuesta se utiliza en el request sign? o ¿se envía un documento a la vez en el request 'upload document' y luego se concatenan estos ids en el request sign?

se envían varios request de documenos en el mismo request de firma

{
    "secret": "924968",
    "disable_ltv": true,
    "use_signature_text": true,
    "options": {
        "57428f59-d695-4e11-a13d-d421e5d5c226": {
            "position": "300, 100, 500, 150",
            "page": "0",
            "image": "0a4f48fd-7a86-4e62-801c-22756dc6735a"
        },
        "4d03ba57-da9d-4833-9bb1-645e4efb35e6": {
            "position": "300, 100, 500, 150",
            "page": "0",
            "image": "0a4f48fd-7a86-4e62-801c-22756dc6735a"
        }
    }
}




def upload_document(nombre_documento, carpeta_documento, url_documento, request_oneshot):
    try:

        url = f'http://192.168.1.82:8080/api/v1/document/460126'  
        payload={}
        files = []
        base_path = './media/oneshot/FilesNoFirmados/'
        file_path = os.path.join(base_path, nombre_documento)
        files.append(('file', (nombre_documento, open(file_path,'rb'), 'application/pdf')))
        response = requests.request("POST", url, data=payload, files=files)
        response_parse = json.loads(response.text)
        
        return json.dumps({"success": True, "data": response_parse['details']})
    except Exception as e:
        return json.dumps({"success": False, "error": f"Error en la solicitud: {e}"})






<!-- CODIGO DE ASIGNAR FIRMA CON FALLO DE 5 PX --> 
pdfFiles.forEach((file, docIndex) => {
        document.querySelectorAll(`.pdf-page[data-document-url="${file}"]`).forEach((pageDiv, pageIndex) => {
            const documentUrl = pageDiv.dataset.documentUrl; // Obtener la URL del documento
            const documentName = pageDiv.dataset.documentName; // Obtener el nombre del documento
    
            // Obtener las dimensiones del contenedor de la página renderizada
            const pageRect = pageDiv.getBoundingClientRect();
            const pageWidth = pageRect.width; // Ancho en píxeles del contenedor
            const pageHeight = pageRect.height; // Alto en píxeles del contenedor
    
            // Determinar el alto dinámico en puntos basado en la relación de aspecto
            const standardWidthInPoints = 612; // Ancho estándar en puntos para cualquier documento
            const dynamicHeightInPoints = (pageHeight / pageWidth) * standardWidthInPoints;
    
            // Factores de escala para convertir píxeles a puntos
            const scaleX = standardWidthInPoints / pageWidth;
            const scaleY = dynamicHeightInPoints / pageHeight;
    
            // Procesar los elementos colocados
            pageDiv.querySelectorAll('.dropped-item').forEach((item) => {
                const rect = item.getBoundingClientRect();
    
                // Coordenadas de la esquina inferior izquierda (x1, y1)
                const x1 = (rect.left - pageRect.left) * scaleX;
                const y1 = (pageHeight - (rect.bottom - pageRect.top)) * scaleY;
    
                // Coordenadas de la esquina superior derecha (x2, y2)
                const x2 = (rect.right - pageRect.left) * scaleX;
                const y2 = (pageHeight - (rect.top - pageRect.top)) * scaleY;
    
                // ID del firmante
                const firmanteId = item.dataset.firmanteId;
    
                // Guardar las posiciones ajustadas
                positions.push({
                    firmante_id: firmanteId,
                    document_url: documentUrl || null, // Agregar la URL del documento
                    document_name: documentName || null, // Agregar el nombre del documento
                    page: pageIndex + 1, // Página relativa al documento actual
                    x1: x1.toFixed(2), // Redondear a 2 decimales
                    y1: y1.toFixed(2),
                    x2: x2.toFixed(2),
                    y2: y2.toFixed(2),
                });
            });
        });
    });

    <!-- CODIGO DE ASIGNAR FIRMA CON FALLO DE 5 PX --> 




<!-- VALIDACIÓN DE FORMULARIO -->
            if (form.checkValidity()) {
                
            } else {
                form.classList.add("was-validated");
            }       

            
                
<!-- VALIDACION DE FORMULARIO -->

echo 'Running server with Gunicorn and gevent...'
gunicorn -k gevent --workers 4 --env DJANGO_SETTINGS_MODULE=sistema.settings sistema.wsgi:application --bind 0.0.0.0:8080


echo 'Running server in production mode with Gunicorn and gevent...'
gunicorn -k gevent --workers 4 --threads 2 --timeout 120 \
  --env DJANGO_SETTINGS_MODULE=sistema.settings \
  --bind 0.0.0.0:8080 \
  sistema.wsgi:application




  DOCUMENTACIÓN DE ERRORES:

  Certificado de Jhonatan Galiano estaba vencido
  Certificado de Danny es renovado o DS1
  El certificado de Jhonatan Galiano firmó en el ambiente de pruebas estando vencido
  


