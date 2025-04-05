from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from crispy_forms.bootstrap import StrictButton


class RowFluid(Div):
    css_class = 'row-fluid'


class SpanColumn(Div):
    def __init__(self, column_width, *fields, **kwargs):
        super().__init__(*fields, **kwargs)

        self.css_class = 'col-sm-%d' % column_width
        if 'column_offset' in kwargs:
            self.css_class += ' col-sm-offset-%d' % kwargs.pop('column_offset')
        if 'text_align' in kwargs:
            self.css_class += ' ' + kwargs.pop('text_align')


class HydrogenaseSequenceFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(HydrogenaseSequenceFormHelper, self).__init__(*args, **kwargs)

        self.form_method = 'get'
        self.form_class = 'form form-horizontal'

        self.label_class = 'col-lg-4 text-right'
        self.field_class = 'col-lg-8'

        self.layout = Layout(
            SpanColumn(6,
                RowFluid(
                    'phylum',
                    'order',
                    'organism',
                    'ncbi_accession',
                    'hydrogenase_class'
                )
            ),
            SpanColumn(6,
                RowFluid(
                    'subunits_predicted',
                    'oxygen_tolerance_predicted',
                    'activity_predicted',
                    'metal_centres_predicted'
                )
            ),
            SpanColumn(12,
                RowFluid(
                    StrictButton('Apply', type='submit', css_class='btn-primary'),
                ), column_offset=2
            )
        )
