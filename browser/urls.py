from django.conf.urls import include, url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r"^$", views.IndexView.as_view(), name="index"),
    url(
        r"sequence/(?P<pk>.+)$",
        views.SequenceDetailView.as_view(),
        name="view_sequence",
    ),
    url(
        r"download",
        include(
            [
                url(r"^\.csv$", views.CSVDownloadView.as_view(), name="download_csv"),
                url(
                    r"^\.fasta$",
                    views.FASTADownloadView.as_view(),
                    name="download_fasta",
                ),
            ]
        ),
    ),
    url(
        r"class/(?P<slug>[\w\d-]+)/$",
        views.ClassDetailView.as_view(),
        name="view_class",
    ),
    url(r"^info/", TemplateView.as_view(template_name="fe.html")),  # NOTE: new addition
    url(
        r"^class/fefea1/", TemplateView.as_view(template_name="fefea1.html")
    ),  # NOTE: new addition
]
