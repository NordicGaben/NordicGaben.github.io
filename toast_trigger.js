//$(document).ready(function() {
//    $(".toast").toast('show');
//});

setTimeout(() => {
    var toast = new bootstrap.Toast(document.querySelector('.toast'))
    toast.show()
}, 30_000);