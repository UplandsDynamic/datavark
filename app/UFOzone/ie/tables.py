# tutorial/tables.py
import django_tables2 as tables
from django_q.models import Schedule, Task
from django.utils.html import format_html


class ScheduleTable(tables.Table):
    class Meta:
        model = Schedule
        template_name = "django_tables2/bootstrap.html"
        fields = ("id", "name", "schedule_type", "next_run")


class ResultsTable(tables.Table):
    class Meta:
        model = Task
        template_name = "django_tables2/bootstrap.html"
        fields = ("id", "started", "stopped", "success", "result")

    def render_result(self, value, record):
        return (
            value
            if record["success"]
            else format_html(
                f"Error acquiring data. See more in the <a href='/admin/django_q/failure/{record['id']}'>admin dashboard.</a>"
            )
        )
