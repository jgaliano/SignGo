function setCookie(c_name,value,exdays){
    var exdate=new Date();
    exdate.setDate(exdate.getDate() + exdays);
    var c_value=escape(value) + ((exdays==null) ? "" : "; expires="+exdate.toUTCString());
    document.cookie=c_name + "=" + c_value;
}
setCookie('bit4id-sign','sign',1)


document.addEventListener("DOMContentLoaded", function(){
    msg = document.getElementById('statusDoc').innerText

    if (msg === "Documentos Firmados"){
        document.getElementById('statusDoc').style.color = "green"
    }else{
        document.getElementById('statusDoc').style.color = "red"
    }
})


function closeModal() {
    document.getElementById('overlay').style.display = 'none';
}

function togglePassword(inputId) {
    const passwordInput = document.getElementById(inputId);
    const toggleIcon = document.querySelector(`#${inputId} ~ button i`);
    
    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        toggleIcon.classList.remove("fa-eye");
        toggleIcon.classList.add("fa-eye-slash");
    } else {
        passwordInput.type = "password";
        toggleIcon.classList.remove("fa-eye-slash");
        toggleIcon.classList.add("fa-eye");
    }
}

// OVERLAY
document.addEventListener("DOMContentLoaded", () => {
    if (sessionStorage.getItem("showOverlay") === "true") {
        document.getElementById("overlay").classList.add("d-none"); // Oculta el overlay
        sessionStorage.removeItem("showOverlay"); // Limpia el estado
    }
});

document.querySelectorAll(".validateButton").forEach(button => {
    button.addEventListener("click", function() {
        var miModal = document.getElementById('exampleModal1')
        miModal.style.display = "None"
        document.getElementById("overlay").classList.remove("d-none"); // Mostrar overlay
        sessionStorage.setItem("showOverlay", "true"); // Guardar estado en sessionStorage
    });
});
// OVERLAY

function showAlert(message, type) {
    var wrapper = document.createElement('div');
    wrapper.innerHTML = '<div class="alert alert-' + type + ' alert-dismissible" role="alert">'
        + message + '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>';
    document.getElementById('liveAlertPlaceholder').append(wrapper);

    setTimeout(() => {
        wrapper.querySelector('.alert').classList.add('alert-fadeout');
        setTimeout(() => {
            wrapper.remove();
        }, 10000);
    }, 10000);
}