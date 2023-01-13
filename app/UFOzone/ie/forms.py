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
        label="Reddit data acquisition",
        choices=CADENCE,
        widget=forms.Select(
            attrs={"class": "change-schedule form-control", "id": "REDDIT"}
        ),
    )

    NUFORC = forms.ChoiceField(
        label="NUFORC data acquisition",
        choices=CADENCE,
        widget=forms.Select(
            attrs={"class": "change-schedule form-control", "id": "NUFORC"}
        ),
    )

    def __init__(self, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)

    def _create_schedule(self, config, source_name, schedule):
        Schedule.objects.create(
            func="UFOzone.tasks.get_data",
            args=f"{config}",
            name=f"{source_name}",
            hook="UFOzone.hooks.print_result",
            schedule_type=schedule,  # update with additional options if new options added to config
            repeats=-1,
        )

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
                            self._create_schedule(
                                config, source_name, schedule
                            )  # add new schedule if did not exist
                        elif (
                            Schedule.objects.get(name=source_name).schedule_type
                            == schedule  # no change if remains the same
                        ):
                            logger.info(f"No change to {source_name}")
                        else:
                            logger.info(f"Changing schedule for {source_name} ...")
                            Schedule.objects.filter(
                                name=f"{source_name}"
                            ).delete()  # delete old schedule
                            self._create_schedule(
                                config, source_name, schedule
                            )  # add new schedule
                    except Exception as e:
                        logger.error(
                            f"There was a problem setting the schedule: {str(e)}"
                        )
                else:  # delete schedule
                    logger.info(f"Deleting schedule for {source_name}")
                    Schedule.objects.filter(
                        name=source_name
                    ).delete()  # delete schedule
            except KeyError as e:
                logger.warning(f"There is no form field for source {source_name}")
        return self.cleaned_data
