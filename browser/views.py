from django.views.generic import DetailView, ListView, View
from django.views.generic.detail import SingleObjectMixin

from common.mixins import CSVResponseMixin, FASTAResponseMixin

from .filters import HydrogenaseSequenceFilter
from .forms import HydrogenaseSequenceFormHelper
from .mixins import FilterableMixin, TableMixin
from .models import HydrogenaseClass, HydrogenaseSequence
from .tables import HydrogenaseSequenceTable


class IndexView(TableMixin, FilterableMixin, ListView):
    model = HydrogenaseSequence
    table = HydrogenaseSequenceTable
    filter = HydrogenaseSequenceFilter

    def dispatch(self, request, *args, **kwargs):
        ins = super(IndexView, self).dispatch(request, *args, **kwargs)
        self._filter.form.helper = HydrogenaseSequenceFormHelper()
        return ins

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['table'] = self.get_table(self.get_queryset())
        return context


class ClassDetailView(TableMixin, SingleObjectMixin, ListView):
    table = HydrogenaseSequenceTable
    template_name = 'browser/hydrogenaseclass_detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(
            queryset=HydrogenaseClass.objects.select_related()
        )
        return super(ClassDetailView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ClassDetailView, self).get_context_data(**kwargs)
        context['entry'] = self.object
        context['table'] = self.get_table(self.get_queryset())
        return context

    def get_queryset(self):
        return HydrogenaseSequence.objects.filter(
            hydrogenase_class=self.object.name
        )


class SequenceDetailView(DetailView):
    model = HydrogenaseSequence
    context_object_name = 'entry'


class CSVDownloadView(CSVResponseMixin, FilterableMixin, View):
    model = HydrogenaseSequence
    filter = HydrogenaseSequenceFilter

    def get(self, request, *args, **kwargs):
        rows = []
        for row in self.get_queryset():
            fields = []
            for field in HydrogenaseSequence._meta.fields:
                fields.append(getattr(row, field.name))
            rows.append(tuple(fields))

        return self.render_to_csv('hyddb-results.csv', rows)


class FASTADownloadView(FASTAResponseMixin, FilterableMixin, View):
    model = HydrogenaseSequence
    filter = HydrogenaseSequenceFilter

    def get(self, request, *args, **kwargs):
        rows = [(row.ncbi_accession, row.protein_sequence)
                for row in self.get_queryset()]
        return self.render_to_fasta('hyddb-results.fa', rows)
