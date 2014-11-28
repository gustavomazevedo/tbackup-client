django.jQuery(document).ready(function($) {
    var NEW_USER = "0";
    var EXISTING_USER = "1";
    
    $('#id_new_or_existing_user').val('0')
    $('input[name=_save]').val('Criar novo usuário')
    $('input[name=_continue]').remove()
    $('input[name=_addanother]').remove()
    
    $('#id_new_or_existing_user').change(function() {
        if (this.value == NEW_USER) {
            $('.field-email').show()
            $('.field-password2').show()
            $('input[name=_save]').val('Criar novo usuário')
        }
        else {
            $('.field-email').hide()
            $('.field-password2').hide()
            $('input[name=_save]').val('Vincular usuário existente')
        }
    });
    
});