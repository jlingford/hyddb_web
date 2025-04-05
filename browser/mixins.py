from django_tables2 import RequestConfig


class TableMixin(object):
    per_page = 50

    def get_table(self, queryset, **kwargs):
        table = self.table(queryset)
        paginate_config = {'per_page': self.per_page}
        RequestConfig(self.request, paginate=paginate_config).configure(table)
        return table


class FilterableMixin(object):
    filter = None
    context_filter_name = 'filter'

    def dispatch(self, request, *args, **kwargs):
        self._filter = self.filter(
            self.request.GET, queryset=self.model._default_manager.all())
        return super(FilterableMixin, self).dispatch(request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        return self._filter.qs

    def get_context_data(self, **kwargs):
        context = super(FilterableMixin, self).get_context_data(**kwargs)
        context[self.context_filter_name] = self._filter
        return context
