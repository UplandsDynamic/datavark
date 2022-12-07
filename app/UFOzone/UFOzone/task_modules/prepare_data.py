import logging, shutil
from django.conf import settings as s
import pandas as pd
from csv_diff import load_csv, compare
from os.path import exists

logger = logging.getLogger("django")


class PrepareData:
    """
    class to prepare the data CSV. Gets latest n (defined in settings)
    rows of data from the downloaded CSV and compares that with the
    previously downloaded CSV. The differences are returned.
    """

    def __new__(cls, source=""):
        obj = super().__new__(cls)
        obj._source = source
        obj._filename_full = source["data_path"]
        obj._filename_latest = source["data_path_latest"]
        obj._prev_filename_latest = source["data_path_prev_latest"]
        return obj._prepare_csv()

    def _copy_latest(self):
        logger.info(
            f"Copying latest {s.DA_SETTINGS['most_recent_n']} rows (as user defined) of data, to avoid overwrite with new & allow comparison between the two dataset upon next download."
        )
        if exists(self._filename_latest):  # make copy of original data
            shutil.copy2(self._filename_latest, self._prev_filename_latest)
        else:
            logger.warning(
                f"No existing latest 'n' REDDIT data to copy at {self._filename_latest}"
            )

    def _prepare_csv(self):
        return_dict = dict()
        logger.info(f"Preparing CSVs for {self._source['source_name']}.")
        # just get latest n rows of new data
        latest_n = pd.read_csv(self._filename_full).head(s.DA_SETTINGS["most_recent_n"])
        latest_n.to_csv(self._filename_latest, index=False)
        if exists(self._prev_filename_latest):
            # compare data from previous pull & put changes in dict
            return_dict = compare(
                load_csv(
                    open(self._prev_filename_latest),
                    key="report_link",
                ),
                load_csv(
                    open(self._filename_latest),
                    key="report_link",
                ),
            )
        else:
            logger.warning(
                f"No previous data file existed, therefore all downloaded data considered new."
            )
            return_dict = {"added": latest_n.to_dict('records')}
        self._copy_latest()  # copy to previous for next time's comparison
        return return_dict
