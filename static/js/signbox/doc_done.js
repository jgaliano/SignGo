function mostrar(data){
    document.getElementById('overlay').style.display = 'flex';
    var caja = document.getElementById('contenedor')
    var embed = document.createElement('embed')
    embed.src = "/media/firmados/" + data
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