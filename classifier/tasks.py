import pandas as pd
from django.conf import settings

import skbio as sk
from hyddb import celery_app

from .classifier import BLASTClassifier
from .models import ClassificationTask
from .cdd import cdd


class KNNClassifierTask(celery_app.Task):
    """Base class for tasks that use k-nearest neighbors for prediction.

    Subclasses must declare :attribute:`evalue_limit` and :attribute:`exceeded_limit_label`.
    All predictions with an E-value higher than :attribute:`evalue_limit` will have
    their prediction set to :attribute:`exceeded_limit_label`.

    The domains that are checked when checking for hydrogenasity are declared in
    :attribute:`hydrogenase_domains`.
    """
    hydrogenase_domains = {
        'Complex1_49kDa superfamily', 
        'Fe_hyd_lg_C',
        'Fe_hyd_lg_C superfamily',
        'HMD',
        'HMD superfamily',
        'HyaB', 
        'NiFeSe_Hases', 
        'cl21493', 
        'FrhA', 
        'HycE2', 
        'NuoD',
    }

    def _enforce_limits(self, table):
        mask_is_null = pd.isnull(table['best_evalue'])
        mask_is_too_high = (table['best_evalue'] > self.evalue_limit)
        mask = (mask_is_null | mask_is_too_high)
        table.loc[mask, 'prediction'] = self.exceeded_limit_label
        return table

    def _check_hydrogenasity(self, ids, sequences):
        assert len(ids) == len(sequences)

        df = cdd(ids, sequences)
        grouped = df.groupby('Query')

        results = []
        for idx in range(1, len(ids) + 1):
            try:
                group = grouped.get_group(idx + 1)
            except KeyError:
                results.append(False)
            else:
                has_hydrogenase_domain = group['Short name'].isin(self.hydrogenase_domains)
                results.append(has_hydrogenase_domain.any())

        assert len(results) == len(ids), 'number of results should be equal to number of entries.'
        return pd.Series(results)

    def classify_sequences(self, ids, sequences, check_hydrogenasity=False):
        results = self.classifier.predict_full(sequences)
        predictions = self.classifier.majority_vote(results)

        grouped = results.groupby('qseqid')
        best_evalue = grouped.evalue.min()

        table = pd.DataFrame({
            'id': ids,
            'prediction': predictions,
            'best_evalue': best_evalue,
        })

        if check_hydrogenasity:
            is_hydrogenase = self._check_hydrogenasity(ids, sequences)
            table.loc[~is_hydrogenase, 'prediction'] = self.exceeded_limit_label
        return self._enforce_limits(table).to_dict(orient='records')


class ClassifyHydrogenaseSequenceTask(KNNClassifierTask):
    """Classifies hydrogenase sequences using k-nearest neighbors."""

    evalue_limit = 1e-3
    exceeded_limit_label = 'NONHYDROGENASE'

    classifier = BLASTClassifier(
        db=settings.BLASTDB,
        no_neighbors=4,
        check_version=False)

    def update_task_with_no_sequences(self, sequences):
        metadata = ClassificationTask.objects.get(pk=self.request.id)
        metadata.no_sequences = len(sequences)
        metadata.save(update_fields=['no_sequences'])

    def run(self, filename, check_sequences):
        entries = list(sk.read(filename, format='fasta'))
        self.update_task_with_no_sequences(entries)

        ids = []
        sequences = []
        for entry in entries:
            entry_id = '{} {}'.format(entry.metadata['id'], entry.metadata['description'])
            entry_sequence = str(entry)

            ids.append(entry_id)
            sequences.append(entry_sequence)

        return self.classify_sequences(ids, sequences, check_sequences)


class ClassifyUpstreamProteinTask(KNNClassifierTask):
    """Classifies upstream protein sequences with 1-nearest neighbors."""

    evalue_limit = 1e-25
    exceeded_limit_label = '[FeFe] Group A1'

    classifier = BLASTClassifier(
        db=settings.DOWNSTREAMDB,
        no_neighbors=1,
        check_version=False)

    def run(self, entries):
        ids, sequences = zip(*entries)
        return self.classify_sequences(ids, sequences)
