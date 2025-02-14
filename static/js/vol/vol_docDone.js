document.addEventListener("DOMContentLoaded", function(){
    // Obtener todos los elementos td con la clase 'valido'
    var tdElements = document.querySelectorAll(".valido");

    // Iterar sobre cada elemento td
    tdElements.forEach(function(tdElement) {
        // Verificar si el texto dentro del td es "Documento Valido"
        if (tdElement.innerHTML.trim() === "Firma Valida") {
            // Si es así, aplicar estilo de color verde
            tdElement.style.color = "green";
        }else{
            tdElement.style.color = "red";
        }
    });
})

function mostrar(data){
    document.getElementById('overlay').style.display = 'flex';
    var caja = document.getElementById('contenedor')
    var embed = document.createElement('embed')
    embed.src = "/media/vol_archivos/" + data
    embed.type = "application/pdf"
    embed.width = "100%"
    embed.height = "500px"
    caja.innerHTML = ''
    caja.appendChild(embed)
    console.log(data)
}

function mostrarInforme(data){
  document.getElementById('overlay').style.display = 'flex';
    var caja = document.getElementById('contenedor')
    var embed = document.createElement('embed')
    embed.src = "/media/vol_informes/" + data
    embed.type = "application/pdf"
    embed.width = "100%"
    embed.height = "500px"
    caja.innerHTML = ''
    caja.appendChild(embed)
    console.log(data)
}

    function closeModal() {
        document.getElementById('overlay').style.display = 'none';
    }