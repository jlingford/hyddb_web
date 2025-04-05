import os.path

from django import forms
from django.core.files.base import ContentFile

from crispy_forms.bootstrap import FormActions, StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Layout, Submit

ALLOWED_EXTS = ['.fasta', '.fa', '.faa']

HORIZONTAL_RULE = HTML('<hr/>')


class ClassificationFormHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super(ClassificationFormHelper, self).__init__(*args, **kwargs)

        self.form_method = 'post'
        self.form_class = 'form'

        self.layout = Layout(
            'sequences',
            'sequences_file',
            HORIZONTAL_RULE,
            'mail_address',
            FormActions(
                StrictButton('Submit Job!', type='submit',
                             css_class='btn-primary')
            )
        )


class ClassificationForm(forms.Form):
    helper = ClassificationFormHelper()

    sequences = forms.CharField(
        label='Sequences', widget=forms.Textarea, required=False)
    sequences_file = forms.FileField(label='Sequences File', required=False)
    mail_address = forms.EmailField(
        label='Mail', required=False,
        help_text=('If an e-mail address is provided, a mail will be sent '
                   'when the job succeeds or fails.')
    )

    def clean(self):
        errors = []

        check = [self.cleaned_data['sequences'],
                 self.cleaned_data['sequences_file']]

        # It is not allowed to upload a file *and* put something in the
        # textarea.
        if not any(check) or all(check):
            errors.append(forms.ValidationError(
                'You must upload either a file of FASTA-formatted sequences '
                'or paste in sequences in FASTA format. You must not fill out '
                'both fields.'
            ))

        # Not really necessary since we don't use the extension, but this may
        # be of help to the user (accidentally uploading the wrong file).
        if self.cleaned_data['sequences_file']:
            ext = os.path.splitext(self.cleaned_data['sequences_file'].name)[1]
            if ext.lower() not in ALLOWED_EXTS:
                errors.append(forms.ValidationError(
                    'The file uploaded must have one of the following '
                    'extensions: %(exts)s, but has the extension %(ext)s.',
                    params={
                        'exts': ', '.join(ALLOWED_EXTS),
                        'ext': ext
                    }
                ))

        if errors:
            raise forms.ValidationError(errors)

    def get_sequences(self):
        """Returns a `ContentFile` with the posted sequences.

        The user either supplied a file or some text in the text area.
        Here we figure out which one they used. File uploads override
        sequences provided in the text area.

        Returns:
            A `ContentFile` object with the posted sequences.
        """

        fileobj = self.cleaned_data['sequences_file']
        if not fileobj:
            fileobj = ContentFile(self.cleaned_data['sequences'])
        return fileobj


class DownstreamProteinSubmissionFormHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super(DownstreamProteinSubmissionFormHelper,
              self).__init__(*args, **kwargs)

        self.form_method = 'post'
        self.form_class = 'form'

        self.form_class = 'form-horizontal'
        self.label_class = 'col-lg-2'
        self.field_class = 'col-lg-8'

        self.add_input(Submit('submit', 'Re-classify'))


class DownstreamProteinSubmissionForm(forms.Form):
    helper = DownstreamProteinSubmissionFormHelper()

    def __init__(self, *args, **kwargs):
        entries = kwargs.pop('entries')
        super(DownstreamProteinSubmissionForm, self).__init__(*args, **kwargs)

        for i, protein in enumerate(entries):
            self.fields['custom_%s' % protein['id']] = forms.CharField(
                label=protein['id'], required=False,
                widget=forms.Textarea(
                    attrs={'class': 'input-sm', 'rows': 2}
                )
            )

    def downstream_proteins(self):
        for name, value in self.cleaned_data.items():
            if name.startswith('custom_') and value != '':
                yield (self.fields[name].label, value)

    def clean(self):
        errors = []

        any_supplied_sequences = any(
            seq for _, seq in self.cleaned_data.items())
        if not any_supplied_sequences:
            errors.append(forms.ValidationError(
                'You must submit one or more downstream protein sequences, '
                'none were supplied.'
            ))

        if errors:
            raise forms.ValidationError(errors)
