function generarReporte(){

    event.preventDefault();

    const form = document.getElementById('filtros-form')
    form.action = '/planilla/generar-reporte/'
    form.submit();
    
    // Mantener la misma URL en la barra de direcciones
    history.pushState(null, '', window.location.href);
}

function filtrar(){
    const form = document.getElementById('filtros-form')
    form.action = '/planilla/reportes/'
    form.submit();
}

document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault(); 
    }
});