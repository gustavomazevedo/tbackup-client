# -*- coding: utf-8 -*-

import os.path
import json
import operator
import requests

from datetime     import timedelta
from hashlib      import sha1 as SHA
from django.conf  import settings
from django.utils import timezone
from client.conf.settings import POST

def json_request(url, method=None, data=None, apikey=None, files=None):
    signed_data = get_signed_data(data, apikey)
    if method == POST:
        r = requests.post(url, data=signed_data, files=files)
    else:
        r = requests.get(url, params=signed_data)
        
    print r
    print r.status_code
    
    if r.status_code != 200:
        #print r.text
        userdir = os.path.expanduser('~')
        with open(os.path.join(userdir ,'Documents', 'untitled.html'), 'wb+') as f:
            f.write(r.text)
        return r.text
    json_response = r.json()
    print json_response
    if r.status_code == 200:
        if authenticated(json_response, apikey):
            return remove_key(json_response, u"signature")
        else:
            from django.http import HttpResponse
            return HttpResponse(u"<h1>Erro de autenticação</h1><h2>Assinatura não válida</h2>")
    else:
        return {}
    
def authenticated(fulldata, apikey):
    signature = fulldata.get(u"signature", None)
    data = remove_key(fulldata, u"signature")
    if not signature:
        return False
    return signature == sign(data, apikey)
    
def sign(data, apikey=None):
    sha1 = SHA()
    if not data:
        sha1.update(u"None")
    else:
        sorted_data = sorted(data.iteritems(),key=operator.itemgetter(0))
        for item in sorted_data:
            sha1.update(unicode(item))
    used_key = apikey or settings.R_SIGNATURE_KEY
    sha1.update(used_key)
    
    #import ipdb; ipdb.set_trace()
    return sha1.hexdigest()

def get_signed_data(data, key):
    return_data = dict(data) if data else {}
    
    return_data[u"timestamp"] = u"%s" % json.dumps(unicode(timezone.now()))
    return_data[u"signature"] = u"%s" % sign(return_data, key)
    
    return return_data

def remove_key(d, key):
    r = dict(d)
    del r[key]
    return r
  
def normalize_time(dt):
  return dt - timedelta(seconds=dt.second) - timedelta(microseconds=dt.microsecond)


def to_hyperlink(hyperlink, display_text=None, attrs=None):
  txt_attrs = ''.join([' {}="{}"'.format(k,v) for k,v in attrs.iteritems()]) if attrs else ''
  txt_display = display_text if display_text else hyperlink
  return '<a href="{}"{}>{}</a>'.format(hyperlink, txt_attrs, txt_display)