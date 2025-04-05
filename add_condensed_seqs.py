import os
import re

import django
from django.db import transaction
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hyddb.settings")
django.setup()

# your imports, e.g. Django models
from browser.models import HydrogenaseSequence


headers = []
sequences = []
with open('data/FeFe Condensed Reference.fas') as fileobj:
    for line in fileobj:
        if line.startswith('>'):
            headers.append(line[1:].strip())
        else:
            sequences.append(line.strip())


seq_map = dict(zip(headers, sequences))

updated = set()
with transaction.atomic():
    for entry in HydrogenaseSequence.objects.all():
        if entry.ncbi_accession in seq_map:
            HydrogenaseSequence.objects.filter(ncbi_accession=entry.ncbi_accession).update(
                sequence_for_classification=seq_map[entry.ncbi_accession]
            )
            updated.add(entry.ncbi_accession)

print(set(headers) - updated)
