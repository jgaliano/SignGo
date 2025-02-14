    const validateButton = document.querySelector(".validateButton");
        const overlay = document.getElementById("overlay");
        const form = document.getElementById("myForm");
        
        validateButton.addEventListener("click", function () {
          const documentoId = sessionStorage.getItem("documentoId"); // Recupera el documentoId
          if (form.checkValidity()) {
            var miModal = document.getElementById('exampleModal');
            miModal.style.display = "none";
        
            overlay.classList.remove("d-none"); // Mostrar overlay
            sessionStorage.setItem("showOverlay", "true"); // Guardar estado en sessionStorage
            const contactos_enviar = document.getElementById('contactos_email')
            enviarCorreo(documentoId, contactos_enviar.value); // REVISAR CAMPO
          } else {
            document.getElementById("overlay").classList.add("d-none"); // Oculta el overlay
            form.classList.add("was-validated");
          }
        });
        
        const exampleModal = document.getElementById('exampleModal');
        exampleModal.addEventListener('show.bs.modal', event => {
          const button = event.relatedTarget;
          const documentoId = button.getAttribute('data-id');
          sessionStorage.setItem("documentoId", documentoId); // Guarda el documentoId
        });
        

        // REQUEST GET TOKEN
        function enviarCorreo(documento_id, correos){
            const documento_enviar = documento_id
            
            
            const data = {
                "request_id_documento": documento_enviar,
                "contactos": correos
            }
        
            fetch('/firma_agil/historial/enviar_correo/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(responseData => {
                // HIDE OVERLAY

                var miModal = document.getElementById('exampleModal')
                miModal.style.display = "block"

                document.getElementById("overlay").classList.add("d-none");
                sessionStorage.removeItem("showOverlay");

                showAlert("Correo Enviado", "success")
        
            })
            .catch(error => {
                document.getElementById("overlay").classList.add("d-none");
                sessionStorage.removeItem("showOverlay");
                alert('Error 500')
            });
        }

        function getCSRFToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]').value;
        }