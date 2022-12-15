from django_q.models import Schedule
from django import forms
import logging
from django_q.models import Schedule
from django_q.tasks import schedule
from django.conf import settings as s

logger = logging.getLogger("django")

_data_sources = s.DA_SETTINGS["data_sources"]


class ScheduleForm(forms.ModelForm):
    REDDIT = forms.BooleanField(
        label="Schedule Reddit data acquisition",
        widget=forms.CheckboxInput(attrs={"class": "change-schedule"}),
        required=False,
    )

    NUFORC = forms.BooleanField(
        label="Schedule NUFORC data acquisition",
        widget=forms.CheckboxInput(attrs={"class": "change-schedule"}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        # add "form-control" class to enable bootstrap - if wanted
        # for name in self.fields.keys():
        #     self.fields[name].widget.attrs.update(
        #         {
        #             "class": "form-control",
        #         }
        #     )

    def save(self):
        for source, config in _data_sources.items():
            logger.info(f"Looking for source: {source}")
            try:
                acquire_data = self.cleaned_data[config["source_name"]]
                logger.info(
                    f"{'Starting' if acquire_data else 'Querying'} {config['source_name']} data acquisition process."
                )
                if acquire_data:
                    try:
                        if not Schedule.objects.filter(
                            name=config["source_name"]
                        ).exists():
                            Schedule.objects.create(
                                func="UFOzone.tasks.get_data",
                                args=f"{config}",
                                name=f"{config['source_name']}",
                                hook="UFOzone.hooks.print_result",
                                schedule_type=Schedule.WEEKLY
                                if config["download_schedule"] == "WEEKLY"
                                else Schedule.DAILY,  # update with additional options if new options added to config
                                repeats=-1,
                            )
                        else:
                            logger.info(
                                f"Schedule for {config['source_name']} is currently running, so not adding to schedule."
                            )
                    except Exception as e:
                        logger.error(
                            f"There was a problem setting the schedule: {str(e)}"
                        )
                else:  # delete schedule
                    Schedule.objects.filter(name=config["source_name"]).delete()
            except KeyError as e:
                logger.warning(
                    f"There is no form field for source {config['source_name']}"
                )
        return self.cleaned_data

    class Meta:
        model = Schedule
        fields = ()  # ("field name",) or __all__ for all fields
