document.addEventListener("DOMContentLoaded", function(){
    btnEnviar = document.getElementById('btn_enviar')
    btnEnviar.classList.add('hidden')
})
document.getElementById('pdf_files').addEventListener('change', function() {
    btnEnviar = document.getElementById('btn_enviar')
    btnEnviar.classList.remove('hidden')
    var input = this;
    var count = input.files ? input.files.length : 0;
    var label = count === 1 ? 'archivo' : 'archivos';
    document.getElementById('archivos_cargados').textContent = count + ' ' + label + ' seleccionado(s)';
    document.getElementById('archivos').style.display = "none"
    document.getElementById('cargar').style.display = "none"
    document.getElementById('box').style.marginTop = "15%"
    document.getElementById('messageError').innerHTML = ""
}); 

function mostrarSpinner() {
    document.getElementById('btn_enviar').style.display = "none"
    var spinner = document.getElementById('spinner');
    var btn1 = document.getElementById('button1');
    var btn2 = document.getElementById('button2');
    spinner.classList.remove('hidden');
    btn1.classList.add('hidden');
    btn2.classList.add('hidden');
    setInterval(incrementarBarra, 100);
}
function ocultarSpinner() {
    var spinner = document.getElementById('spinner');
    spinner.classList.add('hidden');
}