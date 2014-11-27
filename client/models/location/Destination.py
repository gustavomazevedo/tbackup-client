# -*- coding: utf-8 -*-

from requests.exceptions import ConnectionError

from django.db import models

class Destination(models.Model):
    
    class Meta:
        abstract = True
#    """
#    """
#    name = models.CharField(max_length=1024,
#                            verbose_name=u"nome",
#                            primary_key=True)
#
#    class Meta:
#        app_label = 'client'
#        verbose_name = u"destino"
#        ordering = [u"name"]
#
#    def __unicode__(self):
#        return self.name
#
#    @staticmethod
#    def update(web_server, origin_id):
#        try:
#            destinations = web_server \
#                           .destinations(origin_id) \
#                           .get('destinations', None)
#        except ConnectionError: 
#            return #retorna silenciosamente (considera os destinos já cadastrados)
#
#        #define quais destinations podem ser deletados
#        dests_to_delete = [
#            d
#            for d in Destination.objects.exclude(name__in=destinations)
#            if not any(s.destination == d for s in Schedule.objects.all())
#        ]
#        for dest in dests_to_delete:
#            dest.delete()
#        #coleta todos os destinations ainda não cadastrados
#        dests_to_add = [
#            dn
#            for dn in destinations
#            if not any(dn == d.name for d in Destination.objects.all())
#        ]
#        for destname in dests_to_add:
#            Destination.objects.create(name=destname)
