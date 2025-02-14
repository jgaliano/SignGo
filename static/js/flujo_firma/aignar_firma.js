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