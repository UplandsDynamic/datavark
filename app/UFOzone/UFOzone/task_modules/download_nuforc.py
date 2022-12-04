import shutil, datetime, logging, subprocess
from django.conf import settings as s

logger = logging.getLogger("django")


class DownloadNUFORC:

    _data = []
    _current_data_csv_path = s.IE_SETTINGS["data_sources"]["nuforc"]["data_path"]
    _prev_data_csv_path = s.IE_SETTINGS["data_sources"]["nuforc"]["data_path_prev"]
    _data_archive_root = s.IE_SETTINGS["data_sources"]["nuforc"]["data_path_archive"]
    _scraper_path = s.IE_SETTINGS["data_sources"]["nuforc"]["scraper_path"]

    def __new__(cls, args=None, kwargs={}):
        obj = super().__new__(cls)
        return obj._get_data()

    def _get_data(self):
        try:
            self._archive_data()
            self._copy_data()
            self._scrape_data()
            return 1
        except Exception as e:
            logger.error(
                f"An error occurred during NUFORC data management processes: {str(e)}"
            )
        return 0

    def _scrape_data(self):
        logger.info(f"Scraping data for NUFORC ...")
        subprocess.call(f"dvc --cd {self._scraper_path} repro", shell=True)

    def _archive_data(self):
        logger.info(f"Archiving older NUFORC data.")
        shutil.copy2(
            self._prev_data_csv_path,
            f"{self._data_archive_root}{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.csv",
        )

    def _copy_data(self):
        logger.info(
            f"Copying current NUFORC data to new location to avoid overwrite & facilitate comparison."
        )
        # make copy of original data
        shutil.copy2(self._current_data_csv_path, self._prev_data_csv_path)
