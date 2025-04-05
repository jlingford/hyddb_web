import csv

from django.http import HttpResponse


class CSVResponseMixin(object):

    def render_to_csv(self, filename, data):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename="{0}"'.format(filename)

        writer = csv.writer(response, quotechar='"', delimiter=';',
                            quoting=csv.QUOTE_ALL)

        for row in data:
            writer.writerow(row)
        return response


class FASTAResponseMixin(object):

    def render_to_fasta(self, filename, data):
        response = HttpResponse(content_type='text/fasta')
        response['Content-Disposition'] = \
            'attachment; filename="{0}"'.format(filename)

        for header, sequence in data:
            response.write('>{}\n{}\n'.format(header, sequence))
        return response
