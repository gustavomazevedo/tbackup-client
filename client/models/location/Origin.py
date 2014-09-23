
from django.db import models

class Origin(models.Model):
    name = models.CharField(max_length=1024,
                            verbose_name=u"nome")
    #registered = models.BooleanField(default=False,
    #                                 editable=False,
    #                                 verbose_name=u'registrado')
    remote_id = models.BigIntegerField(editable=False)

    class Meta:
        verbose_name = u"origem"
        verbose_name_plural = u"origem"

    def __unicode__(self):
        return self.name

    @staticmethod
    def get():
        return Origin.objects.filter(pk=1) or None

    #@staticmethod
    #def register(web_server, name):
    #    return web_server.register(name)
    #
    #@staticmethod
    #def check_availability(web_server, name):
    #    return web_server.check_availability(name)
