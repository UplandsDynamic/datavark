import django_tables2 as tables
import ie.models as data_models
from django.utils.html import format_html
import logging

logger = logging.getLogger("django")


class ReportTable(tables.Table):
    """
    Class to create the table showing all
    reports data to the user
    """

    class Meta:
        model = data_models.Report
        template_name = "django_tables2/bootstrap4.html"
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
        order_by = "-id"
        order_by_field = "id"  # or "obs_dates__date" to order by observation date

    obs_colors = tables.Column(order_by="obs_colors__color")
    obs_types = tables.Column(order_by="obs_types__type")
    obs_locs = tables.Column(order_by="obs_locs__place_name")
    obs_dates = tables.Column(order_by="obs_dates__date")
    obs_times = tables.Column(order_by="obs_times__time")

    def render_id(self, value):
        return format_html(f"<a href='{value}'>{value}</a>")

    def render_source_name(self, value):
        return value[0:50] + "..." if len(value) > 53 else value

    def render_source_url(self, value):
        return format_html(
            f"<a href='{value}' target='_blank'>{value[0:15] + '...' if len(value) > 18 else value}</a>"
        )

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
