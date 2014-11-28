django.jQuery(document).ready(function($) {
    
    $('#id_name').prop('disabled', true);
    $('#id_change_password').prop('checked',false);
    $('.field-new_password1').hide()
    $('.field-new_password2').hide()
    
    $('#id_change_password').change(function() {
        if (this.checked) {
            $('.field-new_password1').show()
            $('.field-new_password2').show()
        }
        else {
            $('.field-new_password1').hide()
            $('.field-new_password2').hide()
        }
    });
});