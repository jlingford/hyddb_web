import django_tables2 as tables
from django_tables2.utils import A

from .models import HydrogenaseSequence


class HydrogenaseSequenceTable(tables.Table):

    ncbi_accession = tables.LinkColumn(
        'browser:view_sequence', args=[A('ncbi_accession')])
    hydrogenase_class = tables.LinkColumn('browser:view_class', args=[
                                          A('hydrogenase_class.slug')])

    class Meta:
        model = HydrogenaseSequence
        attrs = {'class': 'table table-striped'}
        fields = [
            'ncbi_accession',
            'organism',
            'hydrogenase_class',
            'phylum',
            'order',
            'activity_predicted',
            'oxygen_tolerance_predicted',
            'subunits_predicted',
            'metal_centres_predicted',
            'accessory_subunits_predicted',
        ]
