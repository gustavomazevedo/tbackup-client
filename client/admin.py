from django.contrib import admin

# Register your models here.

from models import (Destination, Origin, Configuration, WebServer)

admin.site.register(Destination)
admin.site.register(Origin)
admin.site.register(Configuration)
admin.site.register(WebServer)