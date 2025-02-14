
function validar() {
    var campos = document.querySelectorAll('input[type="text"], input[type="number"], input[type="email"], input[type="file"]');
    var valido = true;

    campos.forEach(function(campo) {
        // Excluir campos de usuario, contraseña y código PIN
        if (campo.id !== 'usuario' && campo.id !== 'contraseña' && campo.id !== 'pin' && campo.id !== 'inputApellido2') {
            if (!campo.value) {
                valido = false;
            }
        }
    });

    if (valido) {
        document.getElementById('overlay2').style.display = 'flex';        
    } else {
        alert("Por favor, completa todos los campos necesarios.");
    }
}


function closeModal2() {
    document.getElementById('overlay2').style.display = 'none';
}

function mostrarSpinner() {
    var usuario = document.getElementById("usuario").value;
    var contraseña = document.getElementById("contraseña").value;
    var pin = document.getElementById("pin").value;

    if (usuario && contraseña && pin) {
        var spinner = document.getElementById('spinner');
        var btn1 = document.getElementById('button1');
        var btn2 = document.getElementById('button2');
        spinner.classList.remove('hidden');
        btn1.classList.add('hidden');
        btn2.classList.add('hidden');
        setInterval(incrementarBarra, 100);    
    } else {
        console.log("Campos incompletos")
    }                  
}

function ocultarSpinner() {
    var spinner = document.getElementById('spinner');
    spinner.classList.add('hidden');
}

document.addEventListener('DOMContentLoaded', (event) => {
    const fileInput = document.getElementById('formFile1');
    const fileInput2 = document.getElementById('formFile2');
    const fileInput3 = document.getElementById('formFile3');

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            fileInput.classList.add('completed');
            fileInput.classList.remove('nocompleted');
            fileInput.classList.add('form-control');
        } else {
            fileInput.classList.remove('completed');
        }
    });

    fileInput2.addEventListener('change', () => {
        if (fileInput2.files.length > 0) {
            fileInput2.classList.add('completed');
        } else {
            fileInput2.classList.remove('completed');
        }
    });

    fileInput3.addEventListener('change', () => {
        if (fileInput3.files.length > 0) {
            fileInput3.classList.add('completed');
        } else {
            fileInput3.classList.remove('completed');
        }
    });
});
