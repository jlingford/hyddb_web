import django_tables2 as tables
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify


class PredictionsTable(tables.Table):
    id = tables.Column(verbose_name="ID")
    prediction = tables.Column(verbose_name="Class Prediction")
    best_evalue = tables.Column(verbose_name="Best E-value")

    def render_prediction(self, value):
        if value == 'NONHYDROGENASE':
            return mark_safe(
                '<span class="label label-danger">Non-hydrogenase</span>'
            )
        if value == '[FeFe] Group A':
            return mark_safe(value)

        url = reverse('browser:view_class', kwargs={'slug': slugify(value)})
        return mark_safe('<a href="{}">{}</a>'.format(url, value))

    def render_best_evalue(self, value):
        if str(value) == 'nan':
            return mark_safe('&infin;')
        return value
