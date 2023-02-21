import os, logging
from pathlib import Path
from configparser import ConfigParser

logger = logging.getLogger("django")

BASE_DIR = Path(__file__).resolve().parent.parent

"""
Settings file for DatavArk project
"""

# PRAW settings
PRAW_CONFIG_PATH = os.path.join(BASE_DIR, "secrets", "praw.ini")
PRAW_CONFIG = dict()
try:
    praw_config = ConfigParser()
    praw_config.read(PRAW_CONFIG_PATH)
    PRAW_CONFIG["praw_client_id"] = praw_config.get("DEFAULT", "client_id")
    PRAW_CONFIG["praw_client_secret"] = praw_config.get("DEFAULT", "client_secret")
    PRAW_CONFIG["praw_username"] = praw_config.get("DEFAULT", "username")
    PRAW_CONFIG["praw_password"] = praw_config.get("DEFAULT", "password")
    PRAW_CONFIG["praw_user_agent"] = praw_config.get("DEFAULT", "user_agent")
except Exception as e:
    logger.error(f"There was a problem with the PRAW configuration: {str(e)}")

# Application settings
DA_SETTINGS = {
    # define data sources & their associated app paths
    "data_sources": {
        # NUFORC
        "nuforc": {
            "source_name": "NUFORC",
            "source_desc": "NUFORC dataset",
            "source_root_url": "https://nuforc.org",
            "data_path": os.path.join(
                BASE_DIR,
                "data_collection",
                "nuforc",
                "nuforc_sightings_data",
                "data",
                "processed",
                "nuforc_reports.csv",
            ),
            "data_path_latest": os.path.join(
                BASE_DIR,
                "data_collection",
                "nuforc",
                "nuforc_sightings_data",
                "data",
                "processed",
                "nuforc_reports_latest.csv",
            ),
            "data_path_prev": os.path.join(
                BASE_DIR,
                "data_collection",
                "nuforc",
                "nuforc_sightings_data",
                "data",
                "processed",
                "nuforc_prev.csv",
            ),
            "data_path_prev_latest": os.path.join(
                BASE_DIR,
                "data_collection",
                "nuforc",
                "nuforc_sightings_data",
                "data",
                "processed",
                "nuforc_prev_latest.csv",
            ),
            "data_path_archive": os.path.join(
                BASE_DIR,
                "data_collection",
                "nuforc",
                "nuforc_sightings_data",
                "data",
                "archive",
                f"nuforc_reports_archive_",
            ),
            "scraper_path": os.path.join(
                BASE_DIR,
                "data_collection",
                "nuforc",
                "nuforc_sightings_data",  # acquisition script path
            ),
            "archive_dl_csvs": True,  # whether to archive previously downloaded CSV data files (boolean)
        },
        # Reddit
        "reddit": {
            "source_name": "REDDIT",
            "source_desc": "r/UFOs on Reddit.com",
            "source_root_url": "https://reddit.com",
            "data_path": os.path.join(
                BASE_DIR,
                "data_collection",
                "reddit",
                "reddit_sightings_data",
                "data",
                "processed",
                "reddit_reports.csv",
            ),
            "data_path_latest": os.path.join(
                BASE_DIR,
                "data_collection",
                "reddit",
                "reddit_sightings_data",
                "data",
                "processed",
                "reddit_reports_latest.csv",
            ),
            "data_path_prev": os.path.join(
                BASE_DIR,
                "data_collection",
                "reddit",
                "reddit_sightings_data",
                "data",
                "processed",
                "reddit_prev.csv",
            ),
            "data_path_prev_latest": os.path.join(
                BASE_DIR,
                "data_collection",
                "reddit",
                "reddit_sightings_data",
                "data",
                "processed",
                "reddit_prev_latest.csv",
            ),
            "data_path_archive": os.path.join(
                BASE_DIR,
                "data_collection",
                "reddit",
                "reddit_sightings_data",
                "data",
                "archive",
                f"reddit_reports_archive_",
            ),
            "praw_config": PRAW_CONFIG,  # reference to PRAW configuration
            "archive_dl_csvs": True,  # whether to archive previously downloaded CSV data files
        },
    },
    "active_data_sources": [
        "REDDIT",
        "NUFORC",
    ],  # data sources to use (references source_name in data source config, above)
    "most_recent_n": 500,  # limits how many records to process from latest downloaded data. Set 0 for everything.
    "ner_model_name": "trf-model-best-tuned",  # name of NER model to be used
    "ner_model_path": "Datavark/ner_models/trf-model-best-tuned/",  # path to NER model to be used
    "test_without_pull": 0,  # allows testing by performing all actions except pulling from external source (boolean)
    "total_export_records": 25,  # number of records to export from export view
    "records_to_display_per_page": 25,  # number of records per page to display to user in data view
    "restrict_duplicate_location_extractions": True,  # allows extracting cities & states as combined or separate (boolean)
    "exclude_junked": True,  # whether to exclude records marked as junked
    "exclude_no_date": True,  # whether to exclude record with no date data from display & export
    "exclude_no_time": False,  # whether to exclude record with no time data from display & export
    "exclude_no_loc": True,  # whether to exclude records with no location data from display & export
    "exclude_no_type": False,  # whether to exclude records with no types data from display & export
    "exclude_no_color": False,  # whether to exclude records with no colours data from display & export
    "csv_export_path": os.path.join(
        BASE_DIR, "data_collection", "exports"
    ),  # path for exported CSVs
    "csv_export_filename": "datavark_records.csv",  # filename for exported files
}
