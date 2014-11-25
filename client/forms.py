# -*- coding: utf-8 -*-

from django.forms import widgets
from django import forms
from django.utils.translation import ugettext_lazy as _

from client.models import (Origin, WebServer)

from .constants import TIMEDELTA_CHOICES
from .auth import HTTPTokenAuth

class OriginForm(forms.ModelForm):
    model = Origin
    password1 = forms.CharField(widget=forms.PasswordInput, label=u'Senha')
    password2 = forms.CharField(widget=forms.PasswordInput, label=u'Confirmar senha')
    email    = forms.EmailField()
    
    
    
    def clean(self):
        cleaned_data = super(OriginForm, self).clean()
        
        password1 = cleaned_data.get('password1', None)
        password2 = cleaned_data.get('password2', None)
        
        if not password2:
            raise forms.ValidationError(u'É necessário confirmar a senha.')
        elif password1 != password2:
            raise forms.ValidationError(u'As senhas precisam ser iguais para prosseguir.')
        
        to_create = not Origin.objects.exists() or Origin.objects.get(pk=1).name != cleaned_data['name']
        api = None
        api_method = None
        #ao criar, checar se nome ja existe, e usar autenticacao padrao
        if to_create:
            api = WebServer.instance().get_api()
            response_data = api.users.get(username=cleaned_data['name'])
            available = response_data.get('available', None)
            if available is None:
                raise forms.ValidationError(u"Não foi possível conectar-se ao servidor")
            elif available == False:
                raise forms.ValidationError(u"Nome já está sendo utilizado. Por favor, escolha um novo nome ou contacte os administradores.")
            
            api_method = api.users.post
        else:
            #usar autenticacao do usuario cadastrado
            origin = Origin.objects.get(pk=1)
            auth = HTTPTokenAuth(origin.auth_token)
            api = WebServer.instance().get_api(auth)
            api_method = api.users.put
        
        remote_user = {
            'username': cleaned_data['name'],
            'password': cleaned_data['password1'],
            'email': cleaned_data['email']
        }
        
        try:
            result = api_method(remote_user)
            if hasattr(result, 'id') and result['username'] == cleaned_data['name']:
                print result
                cleaned_data['auth_token'] = result['auth_token']
                cleaned_data['remote_id'] = result['id']
            else:
                forms.ValidationError(u'Não foi possível cadastrar usuário no sistema remoto. Favor contactar administradores. Erro de validação: %s' % result)
        except Exception as e:
            raise forms.ValidationError(u'Não foi possível cadastrar usuário no sistema remoto. Favor contactar administradores. Erro de comunicação: %s' % e)
        
        return cleaned_data
    
    #def is_valid(self):
    #    print self
    #    print self.name
    #    print self.password
    #    
    #    remote_user = {
    #        'username': self.name,
    #        'password': self.password,
    #    }
    #    
    #    result = {}
    #    try:
    #        result = self.api.users.post(remote_user)
    #        if hasattr(result, 'id') and result['username'] == remote_user['username']:
    #            print result
    #            return super(OriginForm, self).is_valid()
    #    except Exception as e:
    #        print e
    #        return False
    #    
    #    return super(OriginForm, self).is_invalid()

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