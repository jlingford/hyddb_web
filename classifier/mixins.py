from celery.result import AsyncResult
from django.core.exceptions import ImproperlyConfigured

from .utilities import ResultsWrapper, collect_stats


class StatsMixin:
    """Provides statistics of tasks."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = collect_stats()
        return context


class TaskMixin:
    """Provides the `celery.Task` object to the view and context."""

    def dispatch(self, *args, **kwargs):
        task_id = kwargs.pop('task_id', None)
        if task_id is None:
            raise ImproperlyConfigured(
                'TaskMixin subclass requires keyword argument `task_id`.'
            )
        self.task = AsyncResult(task_id)
        self.results = ResultsWrapper(self.task.result)
        return super(TaskMixin, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task'] = self.task
        context['results'] = self.results
        return context
