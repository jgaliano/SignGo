function generarReporte(token){

    event.preventDefault();

    const form = document.getElementById('filtros-form')
    form.action = '/planilla/reporteDetalleEnvio/' + token + '/'
    form.submit();
    
    // Mantener la misma URL en la barra de direcciones
    history.pushState(null, '', window.location.href);
}

function filtrar(token){
    const form = document.getElementById('filtros-form')
    form.action = '/planilla/envio/' + token + '/'
    form.submit();
}


function reenviarCorreo(token) {
    document.getElementById("overlay").classList.remove("d-none");
    const seleccionados = $('.checkbox:checked').map(function () {
        return $(this).data('id'); 
    }).get(); 

    if (seleccionados.length > 0) {
        // Enviar la lista seleccionada al backend con fetch
        fetch('/planilla/reenviarCorreo/' + token + '/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // Agrega CSRF token para seguridad
            },
            body: JSON.stringify({
                tokenAuth: token,  // Utiliza 'token' aquí en lugar de 'tokenAuth'
                seleccionados: seleccionados // Envía el array de IDs seleccionados
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Correos reenviados exitosamente");
                document.getElementById("overlay").classList.add("d-none");
            } else {
                alert("Hubo un problema al reenviar los correos");
                document.getElementById("overlay").classList.add("d-none");
            }
        })
        .catch(error => console.error('Error:', error));
    } else {
        alert("Por favor, selecciona al menos un envío para reenviar el correo.");
        document.getElementById("overlay").classList.add("d-none");
    }
}


// Función para obtener el token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}













document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault(); 
    }
});





function descargarArchivos(token) {
    const seleccionados = $('.checkbox:checked').map(function () {
        return $(this).data('id'); 
    }).get(); 

    if (seleccionados.length > 0) {
        fetch('/planilla/descargarArchivos/' + token + '/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                tokenAuth: token, 
                seleccionados: seleccionados 
            })
        })
        .then(response => {
            if (response.ok) {
                return response.blob(); // Convertir la respuesta a Blob
            } else {
                alert("Hubo un problema al generar los documentos");
                throw new Error("Error al generar el archivo ZIP");
            }
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'archivos_seleccionados.zip';
            document.body.appendChild(a);
            a.click();
            a.remove();
        })
        .catch(error => console.error('Error:', error));
    } else {
        alert("Por favor, selecciona al menos un envío para descargar el archivo.");
    }
}
