import os
import re
import subprocess
import tempfile
from io import StringIO

import numpy as np
import pandas as pd
import skbio as sk
from sklearn.base import BaseEstimator, ClassifierMixin

from classifier.utilities import dump_fasta


def _check_version():
    cmd = " ".join(["blastp", "-version"])
    process = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE)
    first_line = process.stdout.decode("utf8").splitlines()[0]
    match = re.search(r"([0-9]+)\.([0-9]+)\.([0-9]+)", first_line)
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


class BLASTWrapper(object):
    """A wrapper for BLAST+ for protein searching."""

    def __init__(self, db=None, check_version=True):
        required_version = (2, 2, 31)
        if check_version and _check_version() < required_version:
            raise Exception("Required BLAST+ version is {}".format(required_version))
        self.db = db

    def search(self, seqs, max_target_seqs):
        """Returns a pandas `DataFrame` with the search results."""

        cmd = " ".join(
            [
                "blastp",
                "-max_target_seqs {0}".format(max_target_seqs),
                "-db",
                os.path.basename(self.db),
                "-outfmt",
                '"6 qseqid stitle bitscore evalue"',
            ]
        )

        process = subprocess.run(
            cmd,
            shell=True,
            check=True,
            input=dump_fasta(seqs),
            universal_newlines=True,
            stdout=subprocess.PIPE,
            cwd=os.path.dirname(self.db),
        )

        return pd.read_csv(
            StringIO(process.stdout),
            sep="\t",
            names=["qseqid", "stitle", "bitscore", "evalue"],
        )

    def build(self, seqs):
        """Build a database which can later be searched."""

        if self.db is None:
            self.db = os.path.join(tempfile.mkdtemp(), "blast.db")

        cmd = " ".join(
            [
                "makeblastdb",
                "-dbtype",
                "prot",
                "-out",
                os.path.basename(self.db),  # CHANGED - no-docker branch
                # self.db,
                "-title",
                "blast.db",
            ]
        )

        subprocess.run(
            cmd, check=True, shell=True, input=dump_fasta(seqs), universal_newlines=True
        )


def _to_sequence_collection_with_id(X):
    return (sk.Sequence(x, metadata={"id": i}) for i, x in enumerate(X))


def _to_sequence_collection_with_class(X, y):
    seqcol = []
    for i, (this_x, this_y) in enumerate(zip(X, y)):
        metadata = {"id": i, "description": this_y}
        seqcol.append(sk.Sequence(this_x, metadata=metadata))
    return seqcol


class BLASTClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, no_neighbors=1, **kwargs):
        self._blast = BLASTWrapper(**kwargs)

        if no_neighbors < 1:
            raise ValueError(
                "Argument `no_neighbors` must be larger" "than or equal to one."
            )
        self.no_neighbors = no_neighbors

    def fit(self, X, y):
        self._blast.build(_to_sequence_collection_with_class(X, y))
        return self

    def predict_full(self, X):
        if self._blast is None:
            raise Exception("Cannot predict on an unfitted model.")

        seqcol = _to_sequence_collection_with_id(X)

        # Run the search and only ask for `self.no_neighbors` target
        # sequences for each query sequence.
        results = self._blast.search(seqcol, max_target_seqs=self.no_neighbors)

        # Extract the id and class from each search result.
        results["class"] = results.stitle.str.extract(r"[0-9]+ (.+)")

        # Since BLAST+ may not return a result for each query sequence,
        # we have to make sure that all qseqid's are there. We do this
        # by joining the results DataFrame with a DataFrame which
        # contains all of the ids.
        full = pd.DataFrame({"qseqid": range(len(X))})
        results = pd.merge(full, results, how="left", on="qseqid")
        return results

    def majority_vote(self, results):
        """Pick the majority class for each query sequence."""
        return [
            group["class"][: self.no_neighbors].value_counts(dropna=False).idxmax()
            for _, group in results.groupby("qseqid")
        ]

    def predict(self, X):
        results = self.predict_full(X)
        preds = self.majority_vote(results)
        assert len(X) == len(preds)
        return np.array(preds)
