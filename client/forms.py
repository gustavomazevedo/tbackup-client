# -*- coding: utf-8 -*-

from django.forms import widgets
from django import forms
from django.utils.translation import ugettext_lazy as _

from client.models import (Origin, WebServer)

from .constants import TIMEDELTA_CHOICES

class OriginForm(forms.ModelForm):
    model = Origin
    password = forms.PasswordInput()
    api = WebServer.instance().get_api()
    
    def clean(self):
        cleaned_data = super(OriginForm, self).clean()
        
        response_data = self.api.users.get(username=cleaned_data.get(u"name", None))
	available = response_data.get('available', None)
	if available is None:
            raise forms.ValidationError(u"Não foi possível conectar-se ao servidor")
        elif available == False:
            raise forms.ValidationError(u"Nome já está sendo utilizado. Por favor, escolha um novo nome ou contacte os administradores.")
        return cleaned_data
    
    def is_valid(self):
	print self
	print self.name
	print self.password
	
	result = {}
	try:
	    result = self.api.users.post(remote_user)
	except Exception as e:
	    print e
	    raise
	
	return super(OriginForm, self).is_valid()
        
class RegisterForm(forms.ModelForm):
    name = forms.RegexField(max_length=80,
			    label='Nome',
			    regex=r'^[A-Za-z][A-Za-z0-9_.]*',
			    error_message=u'Somente caracteres alfanuméricos e símbolos "_" e ".". \n'
					  u'Primeiro caractere é obrigatoriamente uma letra.')
		
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance().id:
            self.fields['name'].widget.attrs['disabled'] = True
    
        def clean_name(self):
            return self.instance().name
    
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
        
class ConfirmRestoreForm(forms.Form):
    password1 = forms.PasswordInput()
    password2 = forms.PasswordInput()
    
    def __init__(self, *args, **kwargs):
        super(ConfirmRestoreForm, self).__init__(*args, **kwargs)
    
    def clean(self):
	password1 = self.cleaned_data.get('password1')
	password2 = self.cleaned_data.get('password2')
	
	if password1 and password1 != password2:
	    raise forms.ValidationError(_("Passwords don't match"))
	
	return self.cleaned_data