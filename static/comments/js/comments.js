document.addEventListener("DOMContentLoaded", function () {
    const replyForms = document.querySelectorAll('.reply-form');
    replyForms.forEach(replyForm => {
        replyForm.addEventListener('focusout', (event) => {
            if (!replyForm.contains(event.relatedTarget)) {
                replyForm.classList.add('hidden');
            }
        })
    });
})

function showButton(id) {
    const replyForm = document.getElementById("reply-" + id);
    const parentId = replyForm.querySelector('#id_parent_comment_id_'+id);
    parentId.value = id;
    replyForm.classList.remove('hidden');
    replyForm.querySelector('#reply-input').focus();
}