import time
import logging

from io import StringIO

import skbio as sk
import pandas as pd

import requests

from .utilities import dump_fasta_from_pairs


__all__ = ('cdd',)


logger = logging.getLogger(__name__)


BASE_URL = 'https://www.ncbi.nlm.nih.gov/Structure/bwrpsb/bwrpsb.cgi'


class CDDError(Exception):
    ERROR_MESSAGES = {
        1: 'Invalid search ID.',
        2: 'No effective input (usually no query proteins or search ID specified).',
        4: 'Queue manager (qman) service error.',
        5: 'Data is corrupted or no longer available (cache cleaned, etc.).'
    }

    @staticmethod
    def from_status_code(error_code):
        return CDDError(CDDError.ERROR_MESSAGES[error_code])


def _parse_cdd(output):
    df = pd.read_csv(StringIO(output), sep='\t', skiprows=7)
    df['Query'] = df['Query'].str.extract('Q#([0-9]+).*').astype(int)
    return df


def cdd(ids, sequences, smode='live', maxhit=100, tdata='hits', dmode='rep', qdefl=False, cddefl=False):
    queries = dump_fasta_from_pairs(ids, sequences)

    params = {
        'queries': queries,
        'smode': smode,
        'maxhit': maxhit,
        'tdata': tdata,
        'dmode': dmode,
        'qdefl': 'false' if not qdefl else 'true',
        'cddefl': 'false' if not cddefl else 'true'
    }

    resp = requests.post(BASE_URL, data=params)
    resp.raise_for_status()

    lines = resp.text.splitlines()
    cdsid = lines[1].split()[1]

    logger.debug('Submitted query to CDD with params. Received id %s.', cdsid)

    while True:
        resp = requests.post(BASE_URL, params={'cdsid': cdsid})
        lines = resp.text.splitlines()

        status = int(lines[3].split()[1])
        logger.debug('Query %s has status %d', cdsid, status)

        if status == 0:
            logger.debug('Query completed!')
            return _parse_cdd(resp.text)

        if status in (1, 2, 4, 5):
            raise CDDError.from_status_code(status)

        logger.debug('Query in progress. Waiting.')
        time.sleep(10)
