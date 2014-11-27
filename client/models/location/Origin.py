# -*- coding: utf-8 -*-

from django.db import models

class Origin(models.Model):
    name = models.CharField(max_length=1024,
                            verbose_name=u"nome")
    email = models.EmailField(null=True)
    auth_token = models.CharField(max_length=64, editable=False)
    remote_id = models.BigIntegerField(editable=False)

    class Meta:
        app_label = 'client'
        verbose_name = u"origem"
        verbose_name_plural = u"origem"

    def __unicode__(self):
        return self.name

    @staticmethod
    def instance():
        return Origin.objects.get(pk=1) if Origin.objects.exists() else None
    
    #@staticmethod
    #def register(web_server, name):
    #    return web_server.register(name)
    #
    #@staticmethod
    #def check_availability(web_server, name):
    #    return web_server.check_availability(name)
