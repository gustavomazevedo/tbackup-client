# -*- coding: utf-8 -*-

import json
import operator
import requests

from datetime    import datetime
from Crypto.Hash import SHA
from django.conf import settings
from .constants  import (
  #GET,
  POST,
)

def json_request(url, method=None, data=None, apikey=None, files=None):
    signed_data = get_signed_data(data, apikey)
    if method == POST:
        #import ipdb; ipdb.set_trace()
        r = requests.post(url, data=signed_data, files=files)
    else:
        #import ipdb; ipdb.set_trace()
        r = requests.get(url, params=signed_data)
        
    print r
    print r.status_code
    
    if r.status_code != 200:
        #print r.text
        with open('~/Documents/untitled.html', 'wb') as f:
            f.write(r.text)
        return r.text
    json_response = r.json()
    print json_response
    if r.status_code == 200:
        if authenticated(json_response, apikey):
            return remove_key(json_response, u"signature")
        else:
            import ipdb; ipdb.set_trace()
            from django.http import HttpResponse
            return HttpResponse(u"<h1>Erro de autenticação</h1><h2>Assinatura não válida</h2>")
    else:
        #import ipdb; ipdb.set_trace()
        return {}
    
def authenticated(fulldata, apikey):
    signature = fulldata.get(u"signature", None)
    data = remove_key(fulldata, u"signature")
    if not signature:
        return False
    return signature == sign(data, apikey)
    
def sign(data, apikey=None):
    sha1 = SHA.new()
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
    
    return_data[u"timestamp"] = u"%s" % json.dumps(unicode(datetime.now()))
    return_data[u"signature"] = u"%s" % sign(return_data, key)
    
    #import ipdb; ipdb.set_trace()
    return return_data

def remove_key(d, key):
    r = dict(d)
    del r[key]
    return r