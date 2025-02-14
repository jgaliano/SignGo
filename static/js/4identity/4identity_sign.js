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

function mostrar(data){
    var caja = document.getElementById('contenedor')
    var embed = document.createElement('embed')
    embed.src = "/media/4identity/4identity_files/" + data
    embed.type = "application/pdf"
    caja.innerHTML = ''
    caja.appendChild(embed)
    console.log(data)
}

function closeModal() {
    document.getElementById('overlay').style.display = 'none';
}