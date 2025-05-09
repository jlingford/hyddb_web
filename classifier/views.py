import os

from django.core.files.storage import FileSystemStorage

from django.core.urlresolvers import reverse

# from django.urls import reverse  # NOTE: added to fix django url error
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import FormView, TemplateView, View
from django_tables2 import RequestConfig

from common.mixins import CSVResponseMixin

from .forms import ClassificationForm, DownstreamProteinSubmissionForm
from .mixins import StatsMixin, TaskMixin
from .models import ClassificationTask
from .tables import PredictionsTable
from .tasks import ClassifyHydrogenaseSequenceTask, ClassifyUpstreamProteinTask
from .utilities import make_random_id

STORAGE = FileSystemStorage()

classify_sequences = ClassifyHydrogenaseSequenceTask()
classify_upstream_protein = ClassifyUpstreamProteinTask()


class ClassificationFormView(StatsMixin, FormView):
    form_class = ClassificationForm
    template_name = "classifier/index.html"

    def form_valid(self, form):
        sequences = form.get_sequences()

        check_sequences = False
        email = form.cleaned_data["mail_address"]

        self.task_id = make_random_id()

        sequences_path = STORAGE.save(self.task_id + ".fa", sequences)
        sequences_path = os.path.join(STORAGE.location, sequences_path)

        # Now save metadata in the database.
        metadata = ClassificationTask(task_id=self.task_id, email_address=email)
        metadata.save()

        # And we can submit the job...
        classify_sequences.apply_async(
            args=(sequences_path, check_sequences), task_id=self.task_id
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("classifier:wait", kwargs={"task_id": self.task_id})


class ResultsView(TaskMixin, TemplateView):
    form_class = DownstreamProteinSubmissionForm
    template_name = "classifier/results.html"

    def _get_context_for_task(self, request):
        table = PredictionsTable(
            data=self.results,
            row_attrs={
                "class": (
                    lambda e: "warning" if self.results.has_high_evalue(e) else ""
                )
            },
        )
        RequestConfig(request).configure(table)

        show_high_evalue_warning = self.results.any_has_high_evalue()
        show_nonhydrogenase_warning = self.results.any_non_hydrogenase()
        context = {
            "table": table,
            "show_nonhydrogenase_warning": show_nonhydrogenase_warning,
            "show_high_evalue_warning": show_high_evalue_warning,
        }

        return context

    def get(self, request, *args, **kwargs):
        context = self._get_context_for_task(request)

        entries = self.results.get_group("[FeFe] Group A")
        if not entries:
            form = None
        else:
            form = self.form_class(entries=entries)

        context["form"] = form
        context["task"] = self.task
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(
            request.POST,
            request.FILES,
            entries=self.results.get_group("[FeFe] Group A"),
        )

        # Must call is_valid(), otherwise the cleaned_data attribute will not
        # be available on the form object (and cleaned_data is used by
        # downstream_proteins()).
        if not form.is_valid():
            context = self._get_context_for_task(request)
            context["form"] = form
            return render(request, self.template_name, context)

        downstream_proteins = list(form.downstream_proteins())

        new_task_id = make_random_id()

        metadata = ClassificationTask.objects.get(pk=self.task.id)
        metadata.downstream_protein_task_id = new_task_id
        metadata.save()

        task = classify_upstream_protein.apply_async(
            args=(downstream_proteins,), task_id=new_task_id
        )
        return redirect("classifier:wait", task.id)


class WaitView(TaskMixin, TemplateView):
    template_name = "classifier/wait.html"


class FailureView(TaskMixin, TemplateView):
    template_name = "classifier/failure.html"


def status(request, task_id=None):
    task = classify_sequences.AsyncResult(task_id)
    return JsonResponse({"status": task.status})


class CSVDownloadView(CSVResponseMixin, View):
    def get(self, request, *args, **kwargs):
        task = classify_sequences.AsyncResult(kwargs["task_id"])
        rows = [(r["id"], r["prediction"]) for r in task.result]
        return self.render_to_csv("hyddb-results.csv", rows)
