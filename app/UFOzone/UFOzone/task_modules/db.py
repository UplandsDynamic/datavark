from ie.models import Report, Loc, Date, Time, Color, Type
import logging
from .postprocess import PostProcess
from django.conf import settings

logger = logging.getLogger("django")


class WriteToDB:

    """
    Write the data to the model (insert into database)
    """

    def __new__(cls, data=[]):
        obj = super().__new__(cls)
        obj.data = data
        return obj._insert_data()

    def _insert_data(self):
        logger.info(f"Inserting data into database.")
        errors = []
        # write to database, one doc (observation report) at a time
        for doc in self.data:
            try:
                self._write_to_database(data=doc)
            except Exception as e:
                errors.append(e)
        success_report = (
            f"There were some errors writing to the database: {' | '.join([str(e) for e in errors])}"
            if errors
            else "All records were successfully databased."
            if self.data
            else "There was no data to process!"
        )
        return success_report

    def _write_to_database(self, data):
        # create a report object
        report = Report.objects.create(
            source_name=data["source_name"],
            source_url=data["source_url"],
            obs_txt=data["obs_txt"],
        )
        # create the relations if do not already exist

        for _loc in data["obs_locs"]:
            loc, created = Loc.objects.get_or_create(
                place_name=_loc["place_name"].upper(),
                coordinates=_loc["coordinates"],  # order is Long,Lat
            )
            report.obs_locs.add(loc)

        # datetime.datetime.strptime("01-10-2023", "%d-%m-%Y")
        for _date in data["obs_dates"]:
            date, created = Date.objects.get_or_create(date=_date)
            report.obs_dates.add(date)

        # datetime.datetime.strptime("15:26", "%H:%M")
        for _time in data["obs_times"]:
            time, created = Time.objects.get_or_create(time=_time)
            report.obs_times.add(time)

        for _color in data["obs_colors"]:
            color, created = Color.objects.get_or_create(color=_color.upper())
            report.obs_colors.add(color)

        for _type in data["obs_types"]:
            type, created = Type.objects.get_or_create(type=_type.upper())
            report.obs_types.add(type)  # can be multiple, comma separated
