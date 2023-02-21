from django.shortcuts import render
from django.views import View
from django.conf import settings as s
from django_q.models import Schedule
from django_q.tasks import result_group
from django import template
from django_tables2 import SingleTableMixin, LazyPaginator, RequestConfig
from .tables import ScheduleTable, ResultsTable
from django.http import JsonResponse
from .forms import ScheduleForm
import logging

register = template.Library()
logger = logging.getLogger("django")


class IEView(SingleTableMixin, View):
    """
    Main IE view class, that provides the
    scheduling functionality and the
    task log
    """

    _template_name = "ie/index.html"
    _schedule_model = Schedule
    _schedule_table_class = ScheduleTable
    _form_class = ScheduleForm
    _results_table_class = ResultsTable
    paginator_class = LazyPaginator

    # handle GET requests
    def get(self, *args, **kwargs):
        form = self._form_class(initial=self._get_initial_form_values())
        schedule_table = self._schedule_table_class(
            self._schedule_model.objects.all(), prefix="sch-"
        )
        RequestConfig(self.request).configure(schedule_table)
        results_table = self._results_table_class(
            self._get_task_results(), prefix="results-"
        ).paginate(page=self.request.GET.get("page", 1), per_page=5)
        RequestConfig(self.request).configure(results_table)
        context = {
            "schedule_table": schedule_table,
            "results_table": results_table,
            "request": self.request,
            "form": form,
            "sources": s.DA_SETTINGS["active_data_sources"],
        }
        return render(self.request, self._template_name, context)

    # handle POST requests
    def post(self, *args, **kwargs):
        if self.request.method == "POST":
            form = self._form_class(self.request.POST)
            if form.is_valid():
                data = form.save()
                return JsonResponse(
                    {"success": True, "status_report": data}, status=200
                )
            else:
                return JsonResponse(
                    {"success": False, "status_report": form.errors}, status=400
                )
        return JsonResponse(
            {"success": False, "status_report": "undefined"}, status=400
        )

    def _get_initial_form_values(self):
        initial_values = dict()
        for source, config in s.DA_SETTINGS["data_sources"].items():
            source_name = config["source_name"]
            try:
                schedule = Schedule.objects.filter(name=source_name)[0].schedule_type
                if schedule == "D":
                    initial_value = ScheduleForm.CADENCE[1]
                elif schedule == "W":
                    initial_value = ScheduleForm.CADENCE[2]
            except IndexError:
                initial_value = ScheduleForm.CADENCE[0]
            initial_values[source_name] = initial_value
        return initial_values

    def _get_task_results(self):
        results = []
        for source, config in s.DA_SETTINGS["data_sources"].items():
            try:
                results += result_group(config["source_name"], failures=True).values()
            except AttributeError as e:
                logger.warning(f"No tasks were identified.")
        return results
