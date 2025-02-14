document.addEventListener('DOMContentLoaded', function () {
    const deleteModal = document.getElementById('modal_delete_doc');
    const deleteForm = document.getElementById('deleteForm');

    deleteModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const docId = button.getAttribute('data-id');

        console.log(docId)
        deleteForm.action = deleteForm.action.replace('/0/', `/${docId}/`);
    });
});