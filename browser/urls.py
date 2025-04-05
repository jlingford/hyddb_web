from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'sequence/(?P<pk>.+)$',
        views.SequenceDetailView.as_view(), name='view_sequence'),
    url(r'download', include([
        url(r'^\.csv$', views.CSVDownloadView.as_view(), name='download_csv'),
        url(r'^\.fasta$', views.FASTADownloadView.as_view(), name='download_fasta'),
    ])),
    url(r'class/(?P<slug>[\w\d-]+)/$',
        views.ClassDetailView.as_view(), name='view_class'),
]
