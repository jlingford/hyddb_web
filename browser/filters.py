import django_filters as filters
from django.forms.widgets import SelectMultiple

from .models import HydrogenaseSequence


class AllValuesMultipleChoiceFilter(filters.MultipleChoiceFilter,
                                    filters.AllValuesFilter):
    widget = SelectMultiple


class HydrogenaseSequenceFilter(filters.FilterSet):

    class Meta:
        model = HydrogenaseSequence

        fields = ['ncbi_accession', 'hydrogenase_class', 'organism', 'phylum',
                  'order', 'subunits_predicted', 'activity_predicted',
                  'oxygen_tolerance_predicted']

        help_texts = {}

    hydrogenase_class = AllValuesMultipleChoiceFilter()
    organism = AllValuesMultipleChoiceFilter()
    phylum = AllValuesMultipleChoiceFilter()
    order = AllValuesMultipleChoiceFilter
    subunits_predicted = AllValuesMultipleChoiceFilter()
    ncbi_accession = filters.CharFilter(lookup_type='icontains')
    activity_predicted = AllValuesMultipleChoiceFilter()
    oxygen_tolerance_predicted = AllValuesMultipleChoiceFilter()
    metal_centres_predicted = AllValuesMultipleChoiceFilter()
