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
#from .tasks import get_data
import logging

logger = logging.getLogger('django')

class IEView(View):
    template_name = "ie/index.html"

    def get(self, request, *args, **kwargs):
        template = get_template(self.template_name)
        self.data_scan(1,1)
        context = {"nuforc_data": "Coming soon .."}
        return HttpResponse(template.render(context))

    def data_scan(self, minutes, repeats):
        schedule(
            func='UFOzone.tasks.get_data',
            #get_data,
            source=settings.IE_SETTINGS['data_sources']['nuforc'],
            hook='UFOzone.hooks.print_result',
            schedule_type=Schedule.MINUTES,
            minutes=minutes,
            repeats=repeats,
        )
    
    


# class DetailView(generic.DetailView):
#     model = Report
#     template_name = 'ie/detail.html'
