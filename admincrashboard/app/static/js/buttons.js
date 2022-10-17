
function execute(button, file) {
    button.toggleClass('btn-success btn-primary');
    button.html('<i class="fas fa-spinner fa-spin"></i>')
    
    $.get( "/execute", { button: file } )
    .done(function( data ) {
        button.parent().parent().next().children().children().text(`${data}`);
    })
    .fail(function() {
        button.parent().parent().next().html(`<div><div class="alert alert-danger" role="alert">Some error happened executing the script!</div></div>`);
    }).always(function() {
        button.toggleClass('btn-primary btn-success');
        button.html('<i class="fa-solid fa-play"></i>');
        button.parent().parent().next().removeClass("d-none");
        
    });
    
    return false;
}