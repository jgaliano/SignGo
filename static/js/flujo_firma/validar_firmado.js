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

function mostrar(data, carpeta) {
    var caja = document.getElementById('contenedor');
    var divButton = document.getElementById('buttonDownload');
    caja.innerHTML = ''; 
    divButton.innerHTML = '';

    // Construye la URL del archivo PDF
    var pdfUrl = carpeta;

    // Detecta si el navegador está en un dispositivo móvil
    var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

    if (!isMobile) {
        // Para navegadores de escritorio, usar el elemento <object>
        var object = document.createElement('object');
        object.data = pdfUrl;
        object.type = "application/pdf";
        object.width = "100%";
        object.height = "80vh";
        caja.appendChild(object);
    } else {
        // Botón de descarga para móviles
        var createButton = document.createElement('a');
        createButton.innerText = 'Descargar PDF';
        createButton.href = pdfUrl;
        createButton.classList.add('btn', 'btn-dark');
        divButton.appendChild(createButton);

        // Inicializa PDF.js y carga el archivo PDF
        var pdfjsLib = window['pdfjs-dist/build/pdf'];
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.15.349/pdf.worker.min.js';

        pdfjsLib.getDocument(pdfUrl).promise.then(function(pdfDoc) {
            console.log("El PDF tiene " + pdfDoc.numPages + " páginas.");
            
            for (let pageNum = 1; pageNum <= pdfDoc.numPages; pageNum++) {
                renderPage(pdfDoc, pageNum);
            }
        }).catch(function(error) {
            console.error("Error al cargar el PDF: ", error);
            caja.innerHTML = "<p>Error al cargar el documento PDF.</p>";
        });
    }
}

function renderPage(pdfDoc, pageNum) {
    pdfDoc.getPage(pageNum).then(function(page) {
        var scale = calculateScale();
        var viewport = page.getViewport({ scale: scale });

        var canvas = document.createElement('canvas');
        canvas.classList.add('pdf-canvas'); // Clase para estilos
        canvas.width = viewport.width;
        canvas.height = viewport.height;

        document.getElementById('contenedor').appendChild(canvas);

        var renderContext = {
            canvasContext: canvas.getContext('2d'),
            viewport: viewport
        };

        page.render(renderContext);
    });
}

function calculateScale() {
    var container = document.getElementById('contenedor');
    var containerWidth = container.clientWidth;
    var scale = containerWidth / 700; // Ajusta según el ancho típico de PDF
    return scale > 2 ? 2 : scale; // Evita que la escala sea mayor a 2
}

function closeModal() {
    document.getElementById('overlay').style.display = 'none';
}