function mostrar(data, carpeta, ruta){
    var caja = document.getElementById('contenedor')
    var embed = document.createElement('embed')
    embed.src = "/media/eSignAnyWhere/" + ruta + "/" + carpeta + "/" + data
    embed.type = "application/pdf"
    caja.innerHTML = ''
    caja.appendChild(embed)
    console.log(data)
}

function closeModal() {
    document.getElementById('overlay').style.display = 'none';
}