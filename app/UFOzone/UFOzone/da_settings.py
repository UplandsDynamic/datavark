import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

"""
Settings file for Data Acquisition project
"""

DA_SETTINGS = {
    "data_sources": {
        "nuforc": {
            "source_name": "NUFORC",
            "source_desc": "NUFORC dataset",
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
        },
        "reddit": {
            "source_name": "REDDIT",
            "source_desc": "r/UFOs on Reddit.com",
            "data_path": os.path.join(
                BASE_DIR,
                "data_collection",
                "reddit",
                "reddit_sightings_data",
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
                "reddit",
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
            "scraper_path": os.path.join(
                BASE_DIR, "data_collection", "reddit", "reddit_sightings_data"
            ),
            "geolite_cities_path": os.path.join(
                BASE_DIR,
                "data_collection",
                "reddit",
                "reddit_sightings_data",
                "data",
                "external",
                "cities.csv",
            ),
        },
    },
    "most_recent_n": 500,  # limits how many records to process from latest downloaded data
    "ner_model_name": "trf-model-best-tuned",  # NER model used
    "ner_model_path": "UFOzone/ner_models/trf-model-best-tuned/",  # NER model path
    "test": 0,  # setting to 1 does everything except pull from external source
    "test_source": "nuforc",  # from (currently): 'reddit', 'nuforc'. Only used for post-processing testing
}
