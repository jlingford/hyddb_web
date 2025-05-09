from django.conf.urls import include, url
from django.views.decorators.cache import cache_page, never_cache

from . import views

# app_name = "classifier"  # NOTE: added to fix error

urlpatterns = [
    url(r"^$", views.ClassificationFormView.as_view(), name="index"),
    url(
        r"^jobs/(?P<task_id>[A-z0-9\-]+)/",
        include(
            [
                url(r"wait$", never_cache(views.WaitView.as_view()), name="wait"),
                url(r"status$", never_cache(views.status), name="status"),
                url(
                    r"failure$",
                    cache_page(24 * 60 * 60)(views.FailureView.as_view()),
                    name="failure",
                ),
                url(
                    r"results",
                    include(
                        [
                            url(r"^$", views.ResultsView.as_view(), name="results"),
                            url(
                                r"^\.csv$",
                                views.CSVDownloadView.as_view(),
                                name="download_csv",
                            ),
                        ]
                    ),
                ),
            ]
        ),
    ),
]
