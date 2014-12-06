django.jQuery(document).ready(function($) {
    
    $('#id_username').prop('disabled', true);
    
    //hidden field so django captures value for disabled field
    $('#id_username').each(function() {
        $(this).after(
            '<input type="hidden" name="'  + $(this).attr('name') +
                               '" value="' + $(this).val() +
            '" />');
    });
});