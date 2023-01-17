import os, logging
from pathlib import Path
from configparser import ConfigParser

logger = logging.getLogger("django")

BASE_DIR = Path(__file__).resolve().parent.parent

"""
Settings file for Data Acquisition project
"""

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

DA_SETTINGS = {
    "data_sources": {
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
                BASE_DIR, "data_collection", "nuforc", "nuforc_sightings_data"
            ),
            "archive_dl_csvs": True,  # whether to archive previously downloaded CSV data files
        },
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
            "praw_config": PRAW_CONFIG,
            "archive_dl_csvs": True,  # whether to archive previously downloaded CSV data files
        },
    },
    "active_data_sources": ["REDDIT", "NUFORC"],
    "most_recent_n": 500,  # limits how many records to process from latest downloaded data. Set 0 for everything.
    "ner_model_name": "trf-model-best-tuned",  # NER model used
    "ner_model_path": "DataReaper/ner_models/trf-model-best-tuned/",  # NER model path
    "test_without_pull": 0,  # setting to 1 does everything except pull from external source
    "total_export_records": 25,  # number of records to export from export view
    "restrict_duplicate_location_extractions": True,  # restrict extracting both cities & states as separate entities, etc
    "csv_export_path": os.path.join(
        BASE_DIR, "data_collection", "exports"
    ),  # path for exported CSVs
    "csv_export_filename": "datareaper_records.csv",
}
