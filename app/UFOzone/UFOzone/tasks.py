from django.conf import settings
from .task_modules.ner import Ner
from .task_modules.capture import Capture
from .task_modules.download_nuforc import DownloadNUFORC
from csv_diff import load_csv, compare
import pandas as pd
import logging

logger = logging.getLogger("django_q")
data_dict = dict()

# function to get the data from the data source (CSV files)
def get_data(source=""):
    # if nuforc
    if source == settings.IE_SETTINGS["data_sources"]["nuforc"]:
        if _acquire_data(source):  # run the data acquisition script
            filename_full = settings.IE_SETTINGS["data_sources"]["nuforc"]["data_path"]
            filename_latest = settings.IE_SETTINGS["data_sources"]["nuforc"][
                "data_path_latest"
            ]
            prev_filename = settings.IE_SETTINGS["data_sources"]["nuforc"][
                "data_path_prev"
            ]
            prev_filename_latest = settings.IE_SETTINGS["data_sources"]["nuforc"][
                "data_path_prev_latest"
            ]
            # just get latest n rows
            pd.read_csv(filename_full).head(
                settings.IE_SETTINGS["most_recent_n"]
            ).to_csv(filename_latest)
            # read data from CSV, only get changes from last time & put results in a dict
            new_data = compare(
                load_csv(
                    open(prev_filename_latest),
                    key="report_link",
                ),
                load_csv(
                    open(filename_latest),
                    key="report_link",
                ),
            )
            # create the data dictionary
            data_dict = new_data["added"]
            # get raw text for each doc and put in a list
            doc_texts = _get_text(data_dict)
            # get ents for each doc and put in a list
            doc_ents = _extract_entities(doc_texts)
            # add extracted entities to the data dict
            data_with_ents = _add_ents_to_data(data_dict, doc_ents)
            # finish processing data and write to database
            capture = Capture(data=data_with_ents, source=source)
            result = capture.capture()
            return result
    elif source == settings.IE_SETTINGS["data_sources"]["reddit"]:
        if _acquire_data(source):  # run the data acquisition script
            return "RESULT OF REDDIT DATA ACQUISITION HERE ..."  # as per NUFORC, above
    return f"There was an error retrieving data for {source['source_name']}"


# function to acquire the data
def _acquire_data(source):
    logger.info(f"Acquiring data from {source['source_name']}")
    if source == settings.IE_SETTINGS["data_sources"]["nuforc"]:
        return DownloadNUFORC()  # returns true/false for success/failure
    elif source == settings.IE_SETTINGS["data_sources"]["reddit"]:
        # do reddit here
        return 1


# function to extract the raw text from the data
def _get_text(data_dict):
    doc_texts = []
    for doc in data_dict:
        doc_texts.append(doc["text"])
    return doc_texts


# function to run the NER on the document texts
def _extract_entities(doc_texts):
    ner = Ner(
        model_name="trf-model-best-tuned",
        model_url="UFOzone/ner_models/trf-model-best-tuned/",
        doc_texts=doc_texts,
    )
    return ner.get_entities()


# function to add the extracted entities to the data
def _add_ents_to_data(data_dict, doc_ents):
    for doc, ents in zip(data_dict, doc_ents):
        doc["entities"] = ents
    return data_dict
