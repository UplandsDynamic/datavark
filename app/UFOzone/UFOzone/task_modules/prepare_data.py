import logging
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
        obj.source = source
        obj.filename_full = source["data_path"]
        obj.filename_latest = source["data_path_latest"]
        obj.prev_filename_latest = source["data_path_prev_latest"]
        return obj._prepare_csv()

    def _prepare_csv(self):
        logger.info(f"Preparing CSVs for {self.source['source_name']}.")
        # just get latest n rows of new data
        pd.read_csv(self.filename_full).head(s.DA_SETTINGS["most_recent_n"]).to_csv(
            self.filename_latest
        )
        if exists(self.prev_filename_latest):
            # compare data from previous pull & put changes in dict
            return compare(
                load_csv(
                    open(self.prev_filename_latest),
                    key="report_link",
                ),
                load_csv(
                    open(self.filename_latest),
                    key="report_link",
                ),
            )
        else:
            logger.warning(
                f"No previous data file existed, therefore all downloaded data considered new."
            )
