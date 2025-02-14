document.addEventListener("DOMContentLoaded", function(){
    estado_firma = document.getElementById('estado_firma').innerText
    document.getElementById('con_codigo').style.display = 'none'
    // document.getElementById('btn_ingresar').style.display = 'none'
    document.getElementById('btn_ingresar').style.display = 'block'

    if (estado_firma === "1") {
        document.getElementById('codigoError').style.display = 'none'
    }else{
        document.getElementById('codigoError').style.display = 'block'
        mostrarModal();
    }

    document.getElementById("si_envio").style.display = 'none'

})

function mostrar(data){
    var caja = document.getElementById('contenedor')
    var embed = document.createElement('embed')
    embed.src = "/media/oneshot/FilesNoFirmados/" + data
    embed.type = "application/pdf"
    caja.innerHTML = ''
    caja.appendChild(embed)
    console.log(data)
}

function closeModal() {
    document.getElementById('overlay').style.display = 'none';
}

function mostrarModal(){
    document.getElementById('overlay2').style.display = 'flex';
}

    
function semdOTP(request){     
    document.getElementById('con_codigo').style.display = 'block'
    document.getElementById('btn_ingresar').style.display = 'block'
    const urlBefore = "http://10.10.10.9:8084/api/v1/otp/";
    const idTransaction = document.getElementById('token')
    const idtrans = request
    const url = urlBefore + idtrans;
    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");
    
    const raw = JSON.stringify({
      "delivery_method": "whatsapp"
    });
    
    const requestOptions = {
      method: "POST",
      headers: myHeaders,
      body: raw
    };
    
    fetch(url, {
        method: "POST"
    })
}



    function semdOTPsms(request){
        document.getElementById('con_codigo').style.display = 'block'
        const urlBefore = "http://10.10.10.9:8084/api/v1/otp/";
        const idTransaction = document.getElementById('token')
        const idtrans = request
        const url = urlBefore + idtrans;
        
        const myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        
        const raw = JSON.stringify({
          "delivery_method": "sms"
        });
        
        const requestOptions = {
          method: "POST",
          headers: myHeaders,
          body: raw
        };
        
        fetch(url, {
            method: "POST"
        })

        var countdownElement = document.getElementById('countdown');
        var count = parseInt(countdownElement.textContent);

        function decrementCount() {
            if (count > 0) {
                count--;
                countdownElement.textContent = count;
            } else {
                clearInterval(intervalId);
                document.getElementById("no_envio").style.display = 'none'
                document.getElementById("si_envio").style.display = 'block'
            }
        }
        var intervalId = setInterval(decrementCount, 1000);
    }
    
    function closeModal2() {
        document.getElementById('overlay2').style.display = 'none';
    }

    function validar(){
        document.getElementById('overlay2').style.display = 'flex';
    }

    function mostrarSpinner() {
        document.getElementById('btns_envio').style.display = "none"
        document.getElementById('token_box').style.display = "none"
        document.getElementById('token_box2').style.display = "none"
        var spinner = document.getElementById('spinner');
        var btn1 = document.getElementById('button1');
        var btn2 = document.getElementById('button2');
        spinner.classList.remove('hidden');
        btn1.classList.add('hidden');
        btn2.classList.add('hidden');
        setInterval(incrementarBarra, 100);
    }
    function ocultarSpinner() {
        document.getElementById('btns_envio').style.display = "block"
        var spinner = document.getElementById('spinner');
        spinner.classList.add('hidden');
    }




    // Peticicón Asincrona para request de OTP
    // document.getElementById('boton-peticion').addEventListener('click', function() {
    //     var numero = "{{ request }}";
        
    //     console.log(numero)
    //     console.log("Enviado")

    //     var url = '{% url "sendOtp" %}?numero=' + numero;
    
    //     var xhr = new XMLHttpRequest();
    //     xhr.open('GET', url, true);

    //     document.getElementById('con_codigo').style.display = 'block'
    //     document.getElementById('btn_ingresar').style.display = 'block'

    //     xhr.send();
    // });


    // Peticicón Asincrona para request de OTP
    document.getElementById('boton-peticion2').addEventListener('click', function() {
        var numero = "{{ request }}";

        var url = '{% url "sendOtp" %}?numero=' + numero;
    
        var xhr = new XMLHttpRequest();
        xhr.open('GET', url, true);
    
        //xhr.onload = function() {
        //   if (xhr.status >= 200 && xhr.status < 300) {
        //        document.getElementById('resultado-peticion').innerHTML = xhr.responseText;
        //    } else {
        //        console.error('La petición falló');
        //    }
        //};

        document.getElementById('con_codigo').style.display = 'block'
        document.getElementById('btn_ingresar').style.display = 'block'
    
        //xhr.onerror = function() {
        //    console.error('Error de red');
        //};
    
        xhr.send();
    });
