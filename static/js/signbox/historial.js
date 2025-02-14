function generarReporte(){

    event.preventDefault();

    const form = document.getElementById('filtros-form')
    form.action = '/firma_agil/generar-reporte/'
    form.submit();

    document.getElementById("overlay").classList.add("d-none");
    sessionStorage.removeItem("showOverlay");
    
    // Mantener la misma URL en la barra de direcciones
    history.pushState(null, '', window.location.href);

    
}

function filtrar(){
    const form = document.getElementById('filtros-form')
    form.action = '/firma_agil/historial/'
    form.submit();
}

document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault(); 
    }
});

