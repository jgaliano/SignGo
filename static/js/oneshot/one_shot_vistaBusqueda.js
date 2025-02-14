
document.addEventListener("DOMContentLoaded", function(){
    msg = document.getElementById('statusDoc').innerText

    if (msg === "Documentos Firmados"){
        document.getElementById('statusDoc').style.color = "green"
    }else{
        document.getElementById('statusDoc').style.color = "red"
    }
})

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