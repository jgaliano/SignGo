function mostrar(data){
  var caja = document.getElementById('contenedor')
  var embed = document.createElement('embed')
  embed.src = "/media/oneshot/FilesFirmados/" + data
  embed.type = "application/pdf"
  caja.innerHTML = ''
  caja.appendChild(embed)
  console.log(data)
}

function closeModal() {
    document.getElementById('overlay').style.display = 'none';
}

    function semdOTP(){

        // document.getElementById('overlay2').style.display = 'flex';

        const urlBefore = "http://192.168.11.43/api/v1/otp/";
        const idTransaction = document.getElementById('token')
        const idtrans = idTransaction.innerText
        const url = urlBefore + idtrans;
        
        const raw = JSON.stringify({
            "delivery_method": "whatsapp"
          });
          
          const requestOptions = {
            method: "POST",
            body: raw,
          };

          fetch(url, requestOptions)
          .then(response => {
            if (!response.ok) {
              throw new Error('Hubo un problema con la solicitud: ' + response.status);
            }
            // Manejar la respuesta si la solicitud fue exitosa
            return response.json();
          })
          .then(data => {
            console.log('Respuesta del servidor:', data);
            // Hacer algo con la respuesta del servidor si es necesario
          })
          .catch(error => {
            console.error('Error al realizar la solicitud:', error);
          });
    }
    
    function closeModal2() {
        document.getElementById('overlay2').style.display = 'none';
    }

    function validar(){
        document.getElementById('overlay2').style.display = 'flex';
    }