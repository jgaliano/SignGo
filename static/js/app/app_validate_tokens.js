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



function get_token(){
    document.getElementById("overlay").classList.remove("d-none"); // Mostrar overlay
    sessionStorage.setItem("showOverlay", "true");

    const data = {}

    fetch('/hostIP/tokens/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(responseData => {
        // HIDE OVERLAY
        document.getElementById("overlay").classList.add("d-none");
        sessionStorage.removeItem("showOverlay");
        
        const dataAPI = document.getElementById('data_api')
        // dataAPI.innerText = responseData

        const details = JSON.parse(responseData.data);
        let htmlContent = '<ul>';
        for (const [key, value] of Object.entries(details)) {

            if (typeof value === 'object' && value !== null) {
                htmlContent += `<li><strong>${key}:</strong> <pre>${JSON.stringify(value, null, 2)}</pre></li>`;
            } else {
                htmlContent += `<li><strong>${key}:</strong> ${value}</li>`;
            }
        }
        htmlContent += '</ul>';
        dataAPI.innerHTML = htmlContent;
        // SHOW MODAL2
        var modalElement = document.getElementById('staticBackdrop');
        var modalInstance = new bootstrap.Modal(modalElement);
        modalInstance.show();



    })
    .catch(error => {
        document.getElementById("overlay").classList.add("d-none");
        sessionStorage.removeItem("showOverlay");
        alert('Error 500')
        
    });
}
// REQUEST GET TOKEN

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}