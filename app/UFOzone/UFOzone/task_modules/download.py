import shutil, datetime, logging, subprocess
from django.conf import settings as s
from os.path import exists
from .reddit_scraper import RedditScraper

logger = logging.getLogger("django")


class DownloadNUFORC:

    _data = []
    _current_data_csv_path = s.DA_SETTINGS["data_sources"]["nuforc"]["data_path"]
    _prev_data_csv_path = s.DA_SETTINGS["data_sources"]["nuforc"]["data_path_prev"]
    _data_archive_root = s.DA_SETTINGS["data_sources"]["nuforc"]["data_path_archive"]
    _scraper_path = s.DA_SETTINGS["data_sources"]["nuforc"]["scraper_path"]
    _archive = s.DA_SETTINGS["data_sources"]["nuforc"]["archive_dl_csvs"]

    def __new__(cls, args=None, kwargs={}):
        obj = super().__new__(cls)
        # return success/fail code. Return success without downloading if testing the system
        return 1 if s.DA_SETTINGS["test"] else obj._get_data()

    def _get_data(self):
        try:
            self._archive_data()
            self._copy_data()
            return self._scrape_data()
        except Exception as e:
            logger.error(
                f"An error occurred during NUFORC data management processes: {str(e)}"
            )
        return 0

    def _scrape_data(self):
        logger.info(f"Scraping data for NUFORC ...")
        try:
            subprocess.check_output(f"dvc --cd {self._scraper_path} repro", shell=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"An error occurred during the NUFORC download process: {e}")
        return False

    def _archive_data(self):
        if self._archive:
            logger.info(f"Archiving older NUFORC data.")
            if exists(self._prev_data_csv_path):
                shutil.copy2(
                    self._prev_data_csv_path,
                    f"{self._data_archive_root}{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.csv",
                )
            else:
                logger.warning(
                    f"No NUFORC data to archive at {self._prev_data_csv_path}"
                )
        else:
            logger.info(
                f"Archiving of older downloaded NUFORC data (CSV files) is disabled in configurations."
            )

    def _copy_data(self):
        logger.info(
            f"Copying current NUFORC data to new location to avoid overwrite & facilitate comparison."
        )
        if exists(self._current_data_csv_path):  # make copy of original data
            shutil.copy2(self._current_data_csv_path, self._prev_data_csv_path)
        else:
            logger.warning(
                f"No existing NUFORC data to copy at {self._current_data_csv_path}"
            )


class DownloadReddit:

    _data = []
    _current_data_csv_path = s.DA_SETTINGS["data_sources"]["reddit"]["data_path"]
    _prev_data_csv_path = s.DA_SETTINGS["data_sources"]["reddit"]["data_path_prev"]
    _data_archive_root = s.DA_SETTINGS["data_sources"]["reddit"]["data_path_archive"]
    _archive = s.DA_SETTINGS["data_sources"]["reddit"]["archive_dl_csvs"]

    def __new__(cls, args=None, kwargs={}):
        obj = super().__new__(cls)
        return 1 if s.DA_SETTINGS["test"] else obj._get_data()

    def _get_data(self):
        try:
            self._archive_data()
            self._copy_data()
            return self._scrape_data()
        except Exception as e:
            logger.error(
                f"An error occurred during REDDIT data management processes: {str(e)}"
            )
        return 0

    def _scrape_data(self):
        logger.info(f"Scraping data for REDDIT ...")
        try:
            return RedditScraper()
        except Exception as e:
            logger.error(
                f"An error occurred during the REDDIT download process: {str(e)}"
            )
        return 0

    def _archive_data(self):
        if self._archive:
            logger.info(f"Archiving older REDDIT data.")
            if exists(self._prev_data_csv_path):
                shutil.copy2(
                    self._prev_data_csv_path,
                    f"{self._data_archive_root}{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.csv",
                )
            else:
                logger.warning(
                    f"No REDDIT data to archive at {self._prev_data_csv_path}"
                )
        else:
            logger.info(
                f"Archiving of older downloaded Reddit data (CSV files) is disabled in configurations."
            )

    def _copy_data(self):
        logger.info(
            f"Copying current REDDIT data to new location to avoid overwrite & facilitate comparison."
        )
        if exists(self._current_data_csv_path):  # make copy of original data
            shutil.copy2(self._current_data_csv_path, self._prev_data_csv_path)
        else:
            logger.warning(
                f"No existing REDDIT data to copy at {self._current_data_csv_path}"
            )
