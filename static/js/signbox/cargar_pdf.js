Dropzone.options.myDropzone = {
    paramName: "archivo",
    maxFilesize: 20,
    acceptedFiles: ".pdf",
    init: function () {
        var myDropzone = this;

        this.on("addedfile", function () {
            document.querySelector(".dz-default.dz-message").style.display = "none";
            var numDocumentos = myDropzone.files.length;
            document.getElementById("numDocumentos").textContent = numDocumentos;
            document.getElementById("myModal").style.display = "block";
        });
    },
    dictDefaultMessage: '<i class="fas fa-cloud-upload-alt"></i><p class="mensaje">Arrastra y suelta tus archivos aquí o haz clic para seleccionarlos</p>',
};
 