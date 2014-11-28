django.jQuery(document).ready(function($) {
    var NEW_USER = "0";
    var EXISTING_USER = "1";
    
    $('#id_new_or_existing_user').change(function() {
        if (this.value == NEW_USER) {
            $('.field-email').show()
            $('.field-password2').show()
        }
        else {
            $('.field-email').hide()
            $('.field-password2').hide()
        }
    });
});