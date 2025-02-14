document.getElementById('pdf_files').addEventListener('change', function() {
    var input = this;
    var count = input.files ? input.files.length : 0;
    var label = count === 1 ? 'archivo' : 'archivos';
    document.getElementById('archivos_cargados').textContent = count + ' ' + label + ' seleccionado(s)';
    document.getElementById('archivos').style.display = "none"
    document.getElementById('cargar').style.display = "none"
    document.getElementById('box').style.marginTop = "15%"
    document.getElementById("btn_enviar").disabled = false;
    document.getElementById('messageError').innerHTML = ""
});