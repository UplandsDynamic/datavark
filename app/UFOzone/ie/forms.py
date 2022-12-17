from django_q.models import Schedule
from django import forms
import logging
from django_q.models import Schedule
from django_q.tasks import schedule
from django.conf import settings as s

logger = logging.getLogger("django")

_data_sources = s.DA_SETTINGS["data_sources"]


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ()  # ("field name",) or __all__ for all fields

    CADENCE = (("0", "OFF"), ("1", "DAILY"), ("2", "WEEKLY"))

    # helper function to switch how schedules are expressed
    @staticmethod
    def _config_cadence(cadence):
        if cadence == 1:
            return Schedule.DAILY
        elif cadence == 2:
            return Schedule.WEEKLY

    REDDIT = forms.ChoiceField(
        label="Schedule Reddit data acquisition",
        choices=CADENCE,
        widget=forms.Select(
            attrs={"class": "change-schedule form-control", "id": "REDDIT"}
        ),
    )

    NUFORC = forms.ChoiceField(
        label="Schedule NUFORC data acquisition",
        choices=CADENCE,
        widget=forms.Select(
            attrs={"class": "change-schedule form-control", "id": "NUFORC"}
        ),
    )

    def __init__(self, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)

    def save(self):
        for source, config in _data_sources.items():
            source_name = config["source_name"]
            logger.info(f"Looking for source: {source_name}")
            try:
                cadence = int(self.cleaned_data[source_name])
                logger.info(
                    f"{'Starting' if cadence else 'Querying'} {source_name} data acquisition process."
                )
                if cadence:
                    schedule = self._config_cadence(cadence=int(cadence))
                    try:
                        if not Schedule.objects.filter(name=source_name).exists():
                            Schedule.objects.create(
                                func="UFOzone.tasks.get_data",
                                args=f"{config}",
                                name=f"{source_name}",
                                hook="UFOzone.hooks.print_result",
                                schedule_type=schedule,  # update with additional options if new options added to config
                                repeats=-1,
                            )
                        else:
                            logger.info(
                                f"Changing schedule for {source_name} ..."
                            )
                            Schedule.objects.filter(name=f"{source_name}").update(
                                schedule_type=schedule
                            )
                    except Exception as e:
                        logger.error(
                            f"There was a problem setting the schedule: {str(e)}"
                        )
                else:  # delete schedule
                    logger.info(f"Deleting schedule for {source_name}")
                    Schedule.objects.filter(name=source_name).delete()
            except KeyError as e:
                logger.warning(f"There is no form field for source {source_name}")
        return self.cleaned_data
