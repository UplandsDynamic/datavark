# tutorial/tables.py
import django_tables2 as tables
import ie.models as data_models
from django.utils.html import format_html
import logging

logger = logging.getLogger("django")


class ReportTable(tables.Table):
    class Meta:
        model = data_models.Report
        template_name = "django_tables2/bootstrap.html"
        fields = (
            "id",
            "obs_txt",
            "source_name",
            "source_url",
            "obs_types",
            "obs_colors",
            "obs_locs",
            "obs_dates",
            "obs_times",
        )

    obs_colors = tables.Column(order_by="obs_colors.color")
    obs_types = tables.Column(order_by="obs_types.type")
    obs_locs = tables.Column(order_by="obs_locs.place_name")
    obs_dates = tables.Column(order_by="-obs_dates.date")
    obs_times = tables.Column(order_by="obs_times.time")

    def render_id(self, value):
        return format_html(f"<a href='{value}'>{value}</a>")

    def render_source_name(self, value):
        return value[0:50] + "..." if len(value) > 53 else value

    def render_source_url(self, value):
        return value[0:15] + "..." if len(value) > 18 else value

    def render_obs_txt(self, value):
        return value[0:99] + "..." if len(value) > 102 else value

    def render_obs_colors(self, value):
        return ", ".join([c.color for c in value.all()])

    def render_obs_types(self, value):
        return ", ".join([c.type for c in value.all()])

    def render_obs_locs(self, value):
        return ", ".join([c.place_name for c in value.all()])

    def render_obs_dates(self, value):
        return ", ".join([str(c.date) for c in value.all()])

    def render_obs_times(self, value):
        return ", ".join([str(c.time) for c in value.all()])
