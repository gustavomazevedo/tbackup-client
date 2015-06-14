# -*- coding: utf-8 -*-

from django import forms
from slumber.exceptions import HttpClientError, HttpServerError

from client.models import (Origin, WebServer, Schedule)

NEW_USER = u'0'
EXISTING_USER = u'1'

def try_clean_existing_user(username, password):
    '''usar autenticacao do input do usuário'''
    api = WebServer.instance().get_api(auth=(username, password))

    return try_return_action_result(lambda: api.users.get(username=username)[0])

def try_clean_new_user(user_data):
    '''ao criar, checar se nome ja existe, usando autenticacao padrao para conectar à API'''
    api = WebServer.instance().get_api()
    response_data = api.users.get(username=user_data['username'],
                                  query_type='availability')
    available = response_data.get('available', None)
    if available is None:
        raise forms.ValidationError(u"Não foi possível conectar-se ao servidor")
    elif available == False:
        raise forms.ValidationError(u"Nome já está sendo utilizado. Por favor, escolha um novo nome ou contacte os administradores.")

    return try_return_action_result(lambda: api.users.post(user_data))

def try_return_action_result(action):
    '''Tenta executar ação. Se obtiver sucesso, retorna resultado.
       Caso contrário, captura erros HttpClientError, HttpServerError e Exception (para erros inesperados)
       e aciona erro de validação do form.
    '''
    result = None
    try:
        result = action()
    except HttpClientError as ce:
        raise forms.ValidationError(u'Usuário ou senha inválidos.')
    except HttpServerError as se:
        raise forms.ValidationError(u'Erro Interno no Servidor. Favor contactar administradores. Erro: %s' % se)
    except Exception as e:
        raise forms.ValidationError(u'Erro Inesperado. Favor contactar administradores. Erro: %s' % e)

    return result

def clean_passwords(password1, password2):
    if not password2:
        raise forms.ValidationError(u'É necessário confirmar a senha.')
    elif password1 != password2:
        raise forms.ValidationError(u'Senhas diferentes.')

def clean_result(result):
    if not 'id' in result:
        if isinstance(result, dict) and result.has_key('auth_token'):
            del result['auth_token']
        raise forms.ValidationError(u'Resultado do servidor em formato não esperado: %s' % result)

class OriginAddForm(forms.ModelForm):
    model = Origin

    new_or_existing_user = forms.ChoiceField(
                            label=u'Usuário novo ou existente',
                            choices=((NEW_USER, u'Novo Usuário'),(EXISTING_USER, u'Usuário Existente')))
    name = forms.RegexField(max_length=80,
                label='Nome',
                regex=r'^[A-Za-z][A-Za-z0-9_.]*',
                error_message=u'Somente caracteres alfanuméricos e símbolos "_" e ".". \n'
                      u'Primeiro caractere é obrigatoriamente uma letra.')
    password1 = forms.CharField(widget=forms.PasswordInput, label=u'Senha')
    password2 = forms.CharField(widget=forms.PasswordInput, label=u'Confirmar senha', required=False)
    email    = forms.EmailField(required=False)

    def clean(self):
        cleaned_data = super(OriginAddForm, self).clean()

        new_or_existing_user = cleaned_data.get('new_or_existing_user', None)
        username = cleaned_data.get('name', None)
        password1 = cleaned_data.get('password1', None)
        password2 = cleaned_data.get('password2', None)
        email = cleaned_data.get('email', None)

        print (type(new_or_existing_user), new_or_existing_user)
        if new_or_existing_user == EXISTING_USER:
            result = try_clean_existing_user(username, password1)
        elif new_or_existing_user == NEW_USER:
            #new user
            clean_passwords(password1, password2)
            if not email:
                raise forms.ValidationError(u'Campo e-mail é obrigatório para usuário novo')

            user_data = {
                'username': username,
                'password': password1,
                'email': email
            }

            result = try_clean_new_user(user_data)
        else:
            raise forms.ValidationError(u'Escolha se usuário é novo ou existente')

        clean_result(result)

        cleaned_data['email'] = result['email']
        cleaned_data['auth_token'] = result['auth_token']
        cleaned_data['remote_id'] = result['id']

        return cleaned_data

    def save(self, commit=True):
        obj = super(OriginAddForm, self).save(commit=False)
        obj.auth_token = self.cleaned_data['auth_token']
        obj.remote_id = self.cleaned_data['remote_id']
        if commit:
            obj.save()
        return obj

    class Media:
        js = ('js/origin_add_form.js',)
    class Meta:
        fields = ('new_or_existing_user', 'name', 'email', 'password1', 'password2')

class OriginEditForm(forms.ModelForm):
    model = Origin

    password = forms.CharField(widget=forms.PasswordInput, label=u'Senha atual')
    change_password = forms.BooleanField(label='Modificar senha', required=False)
    new_password1 = forms.CharField(widget=forms.PasswordInput, label=u'Nova senha', required=False)
    new_password2 = forms.CharField(widget=forms.PasswordInput, label=u'Confirmar nova senha', required=False)
    email    = forms.EmailField()

    def clean_name(self):
        '''name is not updatable. If user is willing to change name,
        they must delete existing entry and create another
        '''
        instance = getattr(self, 'instance', None)
        if instance and instance.name and instance.name != self.cleaned_data.get('name', None):
            raise forms.ValidationError(u'Nome não pode ser alterado. Para utilizar um usuário diferente, este deve ser apagado primeiro.')

        return instance.name

    def clean(self):
        cleaned_data = super(OriginEditForm, self).clean()

        username = cleaned_data.get('name', None)
        email = cleaned_data.get('email', None)
        password = cleaned_data.get('password', None)
        change_password = cleaned_data.get('change_password', None)
        new_password1 = cleaned_data.get('new_password1', None)
        new_password2 = cleaned_data.get('new_password2', None)

        #verifica credenciais
        result = try_clean_existing_user(username, password)
        clean_result(result)

        user_data_changes = {'email': email}
        if change_password:
            clean_passwords(new_password1, new_password2)
            user_data_changes['password'] = new_password1

        remote_id = Origin.objects.get(name=username).remote_id
        api = WebServer.instance().get_api((username, password))

        result2 = api.users(remote_id).patch(user_data_changes)
        clean_result(result2)

        cleaned_data['email'] = result2['email']
        cleaned_data['auth_token'] = result2['auth_token']
        cleaned_data['remote_id'] = result2['id']

        return cleaned_data

    def save(self, commit=True):
        obj = super(OriginEditForm, self).save(commit=False)
        obj.auth_token = self.cleaned_data['auth_token']
        obj.remote_id = self.cleaned_data['remote_id']
        if commit:
            obj.save()
        return obj

    class Media:
        js = ('js/origin_edit_form.js',)
    class Meta:
        fields = ('name', 'email', 'password', 'change_password', 'new_password1', 'new_password2')


class ScheduleForm(forms.ModelForm):
    model = Schedule

    #busca no servidor remoto (via API) os destinos disponíveis
    def __init__(self, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)

        token   = Origin.instance().auth_token
        api     = WebServer.instance().get_api(token=token)
        choices = [ (d['name'], d['name']) for d in api.destinations.get() ]

        self.fields['destination'] = forms.ChoiceField(choices=choices)


class ConfirmRestoreForm(forms.Form):
    username = forms.CharField(label=u'Usuário')
    password = forms.CharField(widget=forms.PasswordInput, label=u'Senha')

    def __init__(self, *args, **kwargs):
        super(ConfirmRestoreForm, self).__init__(*args, **kwargs)
        origin = Origin.instance()
        if origin:
            self.fields['username'].initial = origin.name

    def clean(self):
        username = self.cleaned_data.get('username', None)
        password = self.cleaned_data.get('password', None)

        print (username, password)

        try_clean_existing_user(username, password)

        return self.cleaned_data

    class Media:
        js = ('js/restore_confirmation_form.js',)

