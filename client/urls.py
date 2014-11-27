from django.conf.urls import patterns, url

from .views import ConfirmRestoreView

urlpatterns = patterns('client.views' ,
    url(r'^backups/$', 'backups'),
    url(r'^oplogs/$', 'oplogs'),
    url(r'^destinations/$', 'destinations'),
    url(r'^origins/$', 'origins'),
    url(r'^webservers/$', 'webservers'),
    url(r'^rrules/$', 'rrules'),
    url(r'^schedules/$', 'schedules'),
    url(r'^confirm_restore/(?P<pk>[0-9]+)/?$', ConfirmRestoreView.as_view()),
)
