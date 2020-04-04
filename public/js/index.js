$(document).ready(function(){
    $('.sample').click(function(e) {
        var key = e.currentTarget.dataset.key;
        var value = e.currentTarget.dataset.name;
        window.location.search = window.location.search + '&' + key + '=' + value;
    });
});