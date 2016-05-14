function makeConfirmableForms(forms) {
    makeConfirmableFormsWithMessage(forms, "Are you sure?");
}
function makeConfirmableFormsWithMessage(forms, confirmationMessage) {
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

function makeConfirmableLinks(links) {
    makeConfirmableLinksWithMessage(links, "Are you sure?");
}
function makeConfirmableLinksWithMessage(links, confirmationMessage) {
    $(links).on("click", function(e) {
        var link = $(this).attr("href"); // "get" the intended link in a var
        e.preventDefault();
        bootbox.confirm(confirmationMessage, function(result) {
            if (result) {
                document.location.href = link;  // if result, "set" the document location
            }
        });
    });
}
