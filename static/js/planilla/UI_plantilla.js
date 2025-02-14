// Ejemplo de variables
const variables = ["nombre", "apellido", "email", "teléfono", "dirección"];

const variableList = document.getElementById('variable-tags');
const textEditor = document.querySelector('.line');

// Crear etiquetas para cada variable y hacerlas arrastrables
variables.forEach(variable => {
    const tag = document.createElement('div');
    tag.innerText = variable;
    tag.className = 'list-group-item variable-tag';
    tag.setAttribute('draggable', true);
    
    tag.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text', variable);
    });

    variableList.appendChild(tag);
});

// Hacer las líneas del editor de texto receptivas para soltar variables
textEditor.addEventListener('dragover', (e) => {
    e.preventDefault();
});

textEditor.addEventListener('drop', (e) => {
    e.preventDefault();
    const variable = e.dataTransfer.getData('text');
    insertAtCursor({{${variable}}});
});

// Función para insertar texto en la posición del cursor
function insertAtCursor(text) {
    const sel = window.getSelection();
    const range = sel.getRangeAt(0);
    range.deleteContents(); // Opcional: eliminar el texto seleccionado
    const textNode = document.createTextNode(text);
    range.insertNode(textNode);
    range.collapse(false); // Colapsar el rango al final del nuevo nodo
    textEditor.focus(); // Enfocar de nuevo el editor
}

// Función para cambiar el tamaño de fuente
function changeFontSize(select) {
    const size = select.value;
    if (size) {
        document.execCommand('fontSize', false, size);
    }
}

// Función para cambiar el color de fuente
function changeFontColor(select) {
    const color = select.value;
    if (color) {
        document.execCommand('foreColor', false, color);
    }
}

// Función para ajustar la altura del editor
function autoGrow(element) {
    element.style.height = 'auto'; // Restablecer altura
    element.style.height = (element.scrollHeight) + 'px'; // Ajustar a contenido
}