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
import logging

logger = logging.getLogger('django')

class IEView(View):
    template_name = "ie/index.html"

    def get(self, request, *args, **kwargs):
        template = get_template(self.template_name)
        # note: when form set up, move this to be called on POST
        source = settings.IE_SETTINGS['data_sources']['nuforc']
        self.set_data_scan(source=source,minutes=1,repeats=1)
        # return dashboard
        context = {"nuforc_data": "Coming soon .."}
        return HttpResponse(template.render(context))

    def set_data_scan(self, source, minutes, repeats):
        schedule(
            func='UFOzone.tasks.get_data',
            source=source,
            hook='UFOzone.hooks.print_result',
            schedule_type=Schedule.MINUTES,
            minutes=minutes,
            repeats=repeats,
        )
    
    


# class DetailView(generic.DetailView):
#     model = Report
#     template_name = 'ie/detail.html'
