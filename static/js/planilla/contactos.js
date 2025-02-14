 // TABLA CON SELECTORES
 $(document).ready(function () {
    $('#select_all').click(function () {
        if ($(this).is(':checked')) {
            $('.checkbox').prop('checked', true);
        } else {
            $('.checkbox').prop('checked', false);
        }
    });

    $('.checkbox').click(function () {
        if ($('.checkbox:checked').length === $('.checkbox').length) {
            $('#select_all').prop('checked', true);
        } else {
            $('#select_all').prop('checked', false);
        }
    });
});
// TABLA CON SELECTORES

// OVERLAY
document.addEventListener("DOMContentLoaded", () => {
    if (sessionStorage.getItem("showOverlay") === "true") {
        document.getElementById("overlay").classList.add("d-none"); // Oculta el overlay
        sessionStorage.removeItem("showOverlay"); // Limpia el estado
    }
});

document.querySelectorAll(".validateButton").forEach(button => {
    button.addEventListener("click", function() {
        document.getElementById("overlay").classList.remove("d-none"); // Mostrar overlay
        sessionStorage.setItem("showOverlay", "true"); // Guardar estado en sessionStorage
    });
});
// OVERLAY


function showAlert(message, type) {
    var wrapper = document.createElement('div');
    wrapper.innerHTML = '<div class="alert alert-' + type + ' alert-dismissible" role="alert">'
        + message + '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>';
    document.getElementById('liveAlertPlaceholder').append(wrapper);

    setTimeout(() => {
        wrapper.querySelector('.alert').classList.add('alert-fadeout');
        setTimeout(() => {
            wrapper.remove();
        }, 10000);
    }, 10000);
}