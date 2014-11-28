django.jQuery(document).ready(function($) {
    
    $('#id_name').prop('disabled', true);
    
    $('#id_change_password').prop('checked',false);
    $('.field-new_password1').hide()
    $('.field-new_password2').hide()
    $('input[name=_continue]').remove()
    $('input[name=_save]').val('Atualizar')
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
    
    //hidden field so django captures value for disabled field
    $('#id_name').each(function() {
        $(this).after(
            '<input type="hidden" name="'  + $(this).attr('name') +
                               '" value="' + $(this).val() +
            '" />');
    });
});