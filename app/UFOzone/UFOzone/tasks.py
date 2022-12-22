from django.conf import settings as s
from .task_modules.ner import Ner
from .task_modules.db import WriteToDB
from .task_modules.postprocess import PostProcess
from .task_modules.prepare_data import PrepareData
from .task_modules.download import DownloadNUFORC, DownloadReddit
import logging

logger = logging.getLogger("django_q")
data_dict = dict()

# function to get the data from the data source (CSV files)
def get_data(source=""):
    logger.info(f"Acquiring data from {source['source_name']}")
    if source == s.DA_SETTINGS["data_sources"]["nuforc"]:  # if NUFORC
        #return ("TESTING ... REMOVE LINE 16 of tasks.py to resume normal service!")
        data_acquired = DownloadNUFORC()  # returns true/false for success/failure
        if data_acquired:
            prepared_data = PrepareData(source=source)  # prepare the data CSV
            if prepared_data:
                # create the data dictionary
                data = prepared_data["added"]
                # get ents for each doc and add to the data
                data_with_ents = Ner(
                    model_name=s.DA_SETTINGS["ner_model_name"],
                    model_url=s.DA_SETTINGS["ner_model_path"],
                    data_dict=data,
                )
                # post-processing
                processed_data = PostProcess(data=data_with_ents, source=source)
                # write to database
                return WriteToDB(
                    data=processed_data
                )  # return result (success message) to hook
    elif source == s.DA_SETTINGS["data_sources"]["reddit"]:
        #return ("TESTING ... REMOVE LINE 36 of tasks.py to resume normal service!")
        data_acquired = DownloadReddit()  # returns true/false for success/failure
        if data_acquired:
            prepared_data = PrepareData(source=source)  # prepare the data CSV
            if prepared_data:
                # create the data dictionary
                data = prepared_data["added"]
                # get ents for each doc and add to the data
                data_with_ents = Ner(
                    model_name=s.DA_SETTINGS["ner_model_name"],
                    model_url=s.DA_SETTINGS["ner_model_path"],
                    data_dict=data,
                )
                # post-processing
                processed_data = PostProcess(data=data_with_ents, source=source)
                # write to database
                return WriteToDB(
                    data=processed_data
                )  # return result (success message) to hook
    return f"Operation cancelled - no new data acquired for {source['source_name']}."
