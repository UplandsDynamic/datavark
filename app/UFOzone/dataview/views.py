from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings as s
from django import template
from django_tables2 import SingleTableMixin, LazyPaginator, RequestConfig
from .tables import ReportTable
from pathlib import Path
from django.http import FileResponse
import ie.models as data_models
import logging, random, os
import pandas as pd

register = template.Library()
logger = logging.getLogger("django")


class ReportsView(SingleTableMixin, View):

    _template_name = "dataview/reportsview.html"
    _report_model = data_models.Report
    _report_table_class = ReportTable
    paginator_class = LazyPaginator

    def get(self, *args, **kwargs):
        report_table = self._report_table_class(
            self._report_model.objects.all()
        ).paginate(page=self.request.GET.get("page", 1), per_page=15)
        RequestConfig(self.request).configure(report_table)
        _context = {
            "reports_table": report_table,
            "request": self.request,
        }
        return render(self.request, self._template_name, _context)


class DetailView(SingleTableMixin, View):

    _template_name = "dataview/detailview.html"

    def get(self, *args, **kwargs):
        context = dict()
        report_id = kwargs.get("id", None)
        if report_id:
            try:
                report = data_models.Report.objects.filter(id=report_id)[0]
                context = {"report": report}
            except data_models.Report.DoesNotExist:
                logger.error(f"Report ID {report_id} does not exist")
        return render(self.request, self._template_name, context)


class DataExportView(View):
    _template_name = "dataview/dataexportview.html"
    _ds = s.DA_SETTINGS
    _export_path = _ds["csv_export_path"]
    _export_filename = _ds["csv_export_filename"]

    def get(self, *args, **kwargs):
        random_sample = True if self.request.GET.get("random", "") == "true" else False
        source = self.request.GET.get("source", "")
        if self.request.GET.get("download", "false") == "true":
            try:
                self._export_records_csv(self.request, source, random_sample)
                response = FileResponse(
                    open(os.path.join(self._export_path, self._export_filename), "rb")
                )
                response["Content-Disposition"] = (
                    "inline; filename=" + self._export_filename
                )
                return response
            except Exception as e:
                logger.error(f"Data export failed: {str(e)}")
                status = f"Export failed: {str(e)}"
                return render(self.request, self._template_name, {"status": status})
        else:
            return render(self.request, self._template_name, {})

    def _export_records_csv(self, request, source, random_sample):
        # get record list for sources
        records_list = (
            list(data_models.Report.objects.filter(source_name=source.upper()))
            if source
            else list(data_models.Report.objects.all())
        )
        # either export random selection, or all, depending on button user clicked
        records = (
            random.sample(records_list, self._ds["total_export_records"])
            if random_sample
            else records_list
        )
        # create data including from related tables
        data = []
        for report in records:
            data.append(
                {
                    "id": report.id,
                    "record_created": report.record_created,
                    "last_mod": report.last_mod,
                    "source_name": report.source_name,
                    "source_url": report.source_url,
                    "obs_txt": report.obs_txt,
                    "obs_types": [t.type for t in report.obs_types.all()],
                    "obs_colors": [c.color for c in report.obs_colors.all()],
                    "obs_locs": [
                        (
                            l.place_name,
                            {"longitude": l.coordinates.x, "latitude": l.coordinates.y},
                        )
                        for l in report.obs_locs.all()
                    ],
                    "obs_dates": [d.date for d in report.obs_dates.all()],
                    "obs_times": [t.time for t in report.obs_times.all()],
                }
            )
        # df = pd.DataFrame(o.__dict__ for o in records)
        df = pd.DataFrame(data)
        df.to_csv(os.path.join(self._export_path, self._export_filename))
