document.addEventListener("DOMContentLoaded", function(){
    var textos = document.querySelectorAll('.texto');
    textos.forEach(function(texto) {
        if (texto.innerText === "Documentos Firmados") {
            texto.style.color = "green";
        } else {
            texto.style.color = "red";
        }
    });
});