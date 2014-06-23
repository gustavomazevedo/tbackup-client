# -*- coding: utf-8 -*-

from django.forms import widgets
from django import forms

from client.models import (Origin, WebServer)

TIMEDELTA_CHOICES = (
    #(3600, 'hora(s)'),
    (86400,'dia(s)'),
    (604800,'semana(s)'),
    (1296000,'quinzena(s)'),
)

class OriginForm(forms.ModelForm):
    model = Origin
    
    def clean(self):
        cleaned_data = super(OriginForm, self).clean()
        data = WebServer.get().check_availability(cleaned_data.get(u"name", None))
        if data:
            if not data.get(u"availability"):
                raise forms.ValidationError(u"Nome já está sendo utilizado. Por favor, escolha um novo nome ou contacte os administradores.")
        else:
            raise forms.ValidationError(u"Não foi possível conectar-se ao servidor")
        return cleaned_data

class TimedeltaWidget(widgets.MultiWidget):
    def __init__(self, attrs=None):
        widget = (
            widgets.TextInput(attrs={'size': 3, 'maxlength': 3}),
            widgets.Select(choices=TIMEDELTA_CHOICES),
            )
        super(TimedeltaWidget, self).__init__(widget, attrs=attrs)
        
    def decompress(self, value):
        if value:
            for div, name in reversed(TIMEDELTA_CHOICES):
                if value % div == 0:
                    return [str(value / div), str(div)]
        return [None, None]
    
    def format_output(self, rendered_widgets):
        return u''.join(rendered_widgets)

class TimedeltaFormField(forms.MultiValueField):
    widget = TimedeltaWidget
    
    def __init__(self, *args, **kwargs):
        fields = (
            forms.IntegerField(),
            forms.ChoiceField(choices=TIMEDELTA_CHOICES),
        )
        super(TimedeltaFormField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            vals = self._check_values(data_list)
            return vals[0] * vals[1]
        return None
    
    def _check_values(self, values):
        try:
            vals = [int(values[0]), int(values[1])]
            return vals
        except ValueError:
            raise forms.ValidationError(u'Este campo deve receber um número inteiro')
        
class ConfigForm(forms.ModelForm):
    interval = TimedeltaFormField(label=u'Periodicidade')
    
    class Meta:
        exclude = ('last_backup',)
    
    
        
class RegisterForm(forms.ModelForm):
    name = forms.RegexField(
	    max_length=80,
            label='Nome',
	    regex=r'^[A-Za-z][A-Za-z0-9_.]*',
	    error_message=u'Somente caracteres alfanuméricos e símbolos "_" e ".". \n'
                          u'Primeiro caractere é obrigatoriamente uma letra.')
    
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            self.fields['name'].widget.attrs['disabled'] = True
    
        def clean_name(self):
            return self.instance.name
    
    class Meta:
        exclude = ('pvtkey','pubkey',)
    
class LogForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(LogForm, self).__init__(*args, **kwargs)
        self.fields['destination'].widget.attrs['disabled'] = True
        self.fields['date'].widget.attrs['disabled'] = True
        self.fields['filename'].widget.attrs['disabled'] = True
        self.fields['local_status'].widget.attrs['disabled'] = True
        self.fields['remote_status'].widget.attrs['disabled'] = True
        
class RestoreForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(RestoreForm, self).__init__(*args, **kwargs)
        