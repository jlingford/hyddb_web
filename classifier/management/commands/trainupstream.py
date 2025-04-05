import os.path

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import numpy as np
import skbio as sk

from classifier.classifier import BLASTClassifier


def read_sequences(path):
    return np.array([str(seq) for seq in sk.read(path, format='fasta')])


class Command(BaseCommand):

    help = 'Train the upstream protein sequence classifier.'

    def add_arguments(self, parser):
        parser.add_argument('data_dir')

    def handle(self, *args, **options):
        a2_seqs = read_sequences(os.path.join(options['data_dir'], 'Group A2.fasta'))
        a3_seqs = read_sequences(os.path.join(options['data_dir'], 'Group A3.fasta'))
        a4_seqs = read_sequences(os.path.join(options['data_dir'], 'Group A4.fasta'))

        a2_y = np.repeat('[FeFe] Group A2', len(a2_seqs))
        a3_y = np.repeat('[FeFe] Group A3', len(a3_seqs))
        a4_y = np.repeat('[FeFe] Group A4', len(a4_seqs))

        X = np.concatenate([a2_seqs, a3_seqs, a4_seqs])
        y = np.concatenate([a2_y, a3_y, a4_y])

        clf = BLASTClassifier(db=settings.DOWNSTREAMDB)
        clf.fit(X, y)
