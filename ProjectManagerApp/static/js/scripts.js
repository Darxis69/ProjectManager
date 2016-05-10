function makeConfirmableForm(form) {
    form.submit(function(e) {
        var currentForm = this;
        e.preventDefault();
        bootbox.confirm("Are you sure?", function(result) {
            if (result) {
                currentForm.submit();
            }
        });
    });
}