function makeConfirmableForms(forms) {
    makeConfirmableForms(forms, "Are you sure?");
}
function makeConfirmableForms(forms, confirmationMessage) {
    $(forms).submit(function(e) {
        var currentForm = this;
        e.preventDefault();
        bootbox.confirm(confirmationMessage, function(result) {
            if (result) {
                currentForm.submit();
            }
        });
    });
}