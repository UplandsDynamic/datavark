from ie.models import Report, Loc, Date, Time, Color, Type
import logging
from .postprocess import PostProcess
from django.conf import settings
from django.db import IntegrityError

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
            except IntegrityError as e:
                if "duplicate key value violates unique constraint" in str(e):
                    logger.warning("This record was already databased.")
                else:
                    errors.append(e)
            except Exception as e:
                errors.append(e)
        success_report = (
            f"There were some errors writing to the database: {' | '.join([str(e) for e in errors])}"
            if errors
            else "All records were successfully processed."
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


class ClearRelations:

    """
    Clear relations (Many-To-Many field objects) from record.
    """

    def __new__(cls, record_id):
        obj = super().__new__(cls)
        obj.id = record_id
        return obj._clear_extracted_data()

    def _clear_extracted_data(self):
        try:
            report = Report.objects.get(id=self.id)
            # # clear dates
            for d in report.obs_dates.all():
                report.obs_dates.remove(d)
            # clear times
            for t in report.obs_times.all():
                report.obs_times.remove(t)
            # # clear locations
            for l in report.obs_locs.all():
                report.obs_locs.remove(l)
            # clear types
            for t in report.obs_types.all():
                report.obs_types.remove(t)
            # # clear colours
            for c in report.obs_colors.all():
                report.obs_colors.remove(c)
            logger.info(f"Removing data complete ...")
        except Exception as e:
            logger.error(f"Removing data failed: {e}")
            return False
        return True


class JunkRecord:

    """
    Set flag in record to render it "junked" (pending deletion)
    """

    def __new__(cls, record_id):
        obj = super().__new__(cls)
        obj.record_id = record_id
        return obj._set_junked()

    def _set_junked(self):
        try:
            Report.objects.filter(id=self.record_id).update(record_junked=True)
            return f"Record {self.record_id} has been marked as junk!"
        except Exception as e:
            return f"Record junking failed: {e}"


class UpdateDB:

    """
    Update the data model (update database).

    Note: All relations (many-to-many fields references) are cleared in previous step and written anew.
    In the interests of codebase maintainability vis-a-vis the KISS principe (keep it simple stupid),
    this simplifies the update process code, as negates need to determine whether fields have been amended
    or not in client.
    The slight hit on performance of deleting all relations then re-writing is negligible,
    being this is a manual process where only one record is updated at a time.
    Moreover, defaulting to re-writes has the potential to leverage subsequent upgrades of post-processing
    and geocoding code - if desired - thus improving record quality over time.
    """

    def __new__(cls, data=[]):
        """
         Example of incoming data shape:

        {'report_id': 16858, 'obs_txt': 'I saw a greeney blue light hovering above the trees in Sutton, Surrey, UK. It then took off towards London at an incredible speed.', 'obs_dates': [datetime.date(2022, 12, 27)], 'obs_times': [datetime.time(21, 0)], 'obs_types': ['LIGHT'], 'obs_colors': ['GREEN', 'BLUE'], 'obs_locs': [{'place_name': 'LONDON, UK', 'coordinates': <Point object at 0x125356908>}, {'place_name': 'SUTTON, SURREY, UK', 'coordinates': <Point object at 0x125277c08>}]}
        """
        obj = super().__new__(cls)
        obj.data = data
        return obj._insert_data()

    def _insert_data(self):
        logger.info(f"Updating data in database ...")
        errors = []
        # write to database, one doc (observation report) at a time
        try:
            self._write_to_database()
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

    def _write_to_database(self):

        # update the report object.
        report, created = Report.objects.update_or_create(
            id=self.data["report_id"],
            defaults={
                "obs_txt": self.data["obs_txt"]
                # source_name & source_url should not be updated, as they are what they are.
            },
        )

        # # update the relations

        if "obs_locs" in self.data:
            for _loc in self.data["obs_locs"]:
                loc, created = Loc.objects.get_or_create(
                    place_name=_loc["place_name"].upper(),
                    coordinates=_loc["coordinates"],  # order is Long,Lat
                )
                report.obs_locs.add(loc)

        if "obs_dates" in self.data:
            # datetime.datetime.strptime("01-10-2023", "%d-%m-%Y")
            for _date in self.data["obs_dates"]:
                date, created = Date.objects.get_or_create(date=_date)
                report.obs_dates.add(date)

        if "obs_times" in self.data:
            # datetime.datetime.strptime("15:26", "%H:%M")
            for _time in self.data["obs_times"]:
                time, created = Time.objects.get_or_create(time=_time)
                report.obs_times.add(time)

        if "obs_colors" in self.data:
            for _color in self.data["obs_colors"]:
                color, created = Color.objects.update_or_create(color=_color.upper())
                report.obs_colors.add(color)

        if "obs_types" in self.data:
            for _type in self.data["obs_types"]:
                type, created = Type.objects.get_or_create(type=_type.upper())
                report.obs_types.add(type)  # can be multiple, comma separated
