function validar_link(TokenArchivo){
    const overlay = document.getElementById("overlay");

    // MOSTRAR OVERLAY
    overlay.classList.remove("d-none");
    sessionStorage.setItem("showOverlay", "true");

    // OBTENER LINK PÚBLICO O RENOVAR LINK EXPIRADO
    obtener_link(TokenArchivo)
}

function obtener_link(TokenArchivo){
    const token_auth_archivo = TokenArchivo
            
    const data = {
        "token_auth_archivo": token_auth_archivo
    }
        
    fetch('/firma_agil/historial/validar_url/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(responseData => {

        document.getElementById("overlay").classList.add("d-none");
        sessionStorage.removeItem("showOverlay");

        const modalArchivo = document.getElementById('exampleModalFile')
        const modalInstance = new bootstrap.Modal(modalArchivo)
        modalInstance.show();

        const url = responseData.url
        mostrar(url)


        
    })
    .catch(error => {
        document.getElementById("overlay").classList.add("d-none");
        sessionStorage.removeItem("showOverlay");
        alert('Error al abrir el archivo. Por favor intentelo más tarde.')
    });
}

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function mostrar(url){
    var alertWrappers = document.querySelectorAll('.alert-wrapper');
    alertWrappers.forEach(function(wrapper) {
        wrapper.remove();
    });
    var caja = document.getElementById('contenedorFile')
    var embed = document.createElement('embed')
    embed.src = url
    embed.type = "application/pdf"
    caja.innerHTML = ''
    caja.appendChild(embed)
}