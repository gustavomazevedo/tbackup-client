from django.conf.urls import patterns, url

from .views import ConfirmRestoreView

urlpatterns = patterns('client.views' ,
    url(r'^backups/$', 'backups', name='backups'),
    url(r'^schedules/$', 'schedules', name='schedules'),
    url(r'^schedule_change/(?P<id>[0-9]+)/?$', 'schedule_change', name='schedule_change'),
    url(r'^restore/(?P<pk>[0-9]+)/?$', ConfirmRestoreView.as_view(), name='restore'),
)
