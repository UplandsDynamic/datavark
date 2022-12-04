from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import View
from .models import Report
from django.conf import settings
import pandas as pd
from django.template import Template, Context
from django.template.loader import get_template
from django_q.models import Schedule
from django_q.tasks import schedule
from UFOzone.tests import dummy_data
import logging

logger = logging.getLogger("django")


class IEView(View):
    template_name = "ie/index.html"

    def get(self, request, *args, **kwargs):
        template = get_template(self.template_name)
        # note: when form set up, move this to be called on POST & also source defined from there
        source = settings.IE_SETTINGS["data_sources"]["nuforc"]
        self.test() if settings.IE_SETTINGS["test"] else self.set_data_scan(
            source=source, minutes=1, repeats=1
        )
        # return dashboard
        context = {"nuforc_data": "Coming soon .."}
        return HttpResponse(template.render(context))

    def set_data_scan(self, source, minutes, repeats):
        schedule(
            func="UFOzone.tasks.get_data",
            source=source,
            hook="UFOzone.hooks.print_result",
            schedule_type=Schedule.MINUTES,
            minutes=minutes,
            repeats=repeats,
        )

    def test(self):
        # test writing to model (remove all this and uncomment self.set_data_scan above when done)
        from UFOzone.task_modules.capture import Capture

        dummy_sources = {
            "reddit": {
                "source": settings.IE_SETTINGS["data_sources"]["reddit"],
                "data": dummy_data.DUMMY_REDDIT,
            },
            "nuforc": {
                "source": settings.IE_SETTINGS["data_sources"]["nuforc"],
                "data": dummy_data.DUMMY_NUFORC,
            },
        }
        capture = Capture(
            data=dummy_sources[settings.IE_SETTINGS["test_source"]]["data"],
            source=dummy_sources[settings.IE_SETTINGS["test_source"]]["source"],
        )
        result = capture.capture()
        logger.info(result)


# class DetailView(generic.DetailView):
#     model = Report
#     template_name = 'ie/detail.html'
