import datetime
import uuid
from io import StringIO

from django.db.models import Sum

import skbio as sk

from .models import ClassificationTask


def to_generator(iterable):
    return (x for x in iterable)


def dump_fasta(seqs):
    """Dump an iterable of `skbio.Sequence` objects to FASTA format."""
    strio = StringIO()
    sk.write(to_generator(seqs), format='fasta', into=strio)
    return strio.getvalue()


def dump_fasta_from_pairs(ids, sequences):
    """Dump iterables of ids and sequences to FASTA format."""
    strio = StringIO()
    for id, sequence in zip(ids, sequences):
        strio.write('>{}\n'.format(id))
        strio.write(sequence + '\n')
    return strio.getvalue()


def collect_stats():
    date_from = datetime.datetime.now() - datetime.timedelta(days=1)

    jobs_all = ClassificationTask.objects
    jobs_in_day = ClassificationTask.objects.filter(
        submitted_at__gte=date_from
    )

    job_count = jobs_all.count()
    sequence_count = jobs_all.aggregate(
        no_sequences=Sum('no_sequences'))['no_sequences'] or 0

    job_count_in_day = jobs_in_day.count()
    sequence_count_in_day = jobs_in_day.aggregate(
        no_sequences=Sum('no_sequences'))['no_sequences'] or 0

    return {
        'job_count': job_count,
        'sequence_count': sequence_count,
        'job_count_in_day': job_count_in_day,
        'sequence_count_in_day': sequence_count_in_day
    }


def make_random_id():
    return uuid.uuid4().hex


class ResultsWrapper(object):

    def __init__(self, results):
        self._results = results

    def any_non_hydrogenase(self):
        return any(self.is_non_hydrogenase(entry) for entry in self._results)

    def is_non_hydrogenase(self, entry):
        return entry['prediction'] == 'NONHYDROGENASE'

    def any_has_high_evalue(self):
        return any(self.has_high_evalue(entry) for entry in self._results)

    def has_high_evalue(self, entry):
        if 'best_evalue' not in entry:
            return False
        return entry['best_evalue'] > 1e-25

    def get_group(self, group_name):
        return [entry
                for entry in self._results
                if entry['prediction'] == group_name]

    def __iter__(self):
        return iter(self._results)
