from django.conf import settings
from .task_modules.ner import Ner
from csv_diff import load_csv, compare
import pandas as pd
import logging

logger = logging.getLogger("django_q")

FIRST_RUN = 0
data_dict = dict()

""" REMOVE THESE EXAMPLES ONCE DEV DONE!

Example incoming NUFORC data:

 {'summary': 'Viewed some red lights in the sky appearing to be moving north and slower than an airplane.', 'city': 'Visalia', 'state': 'CA', 'date_time': '2021-12-15T21:45:00', 'shape': 'light', 'duration': '2 minutes', 'stats': 'Occurred : 12/15/2021 21:45  (Entered as : 12/15/2021 9:45 PM) Reported: 12/15/2021 10:30:54 PM 22:30 Posted: 12/19/2021 Location: Visalia, CA Shape: Light Duration:2 minutes', 'report_link': 'http://www.nuforc.org/webreports/165/S165881.html', 'text': 'Viewed some red lights in the sky appearing to be moving north and slower than an airplane. Saw multiple red lights moving in the sky in what appeared to be uniform motion, but could be wrong. Lights appeared to be traveling north or northwest slower than a plane. I viewed the phenomenon standing outside the planet fitness gym on Demaree and walnut in visalia CA, and I was facing west while filming them. The weather was cloudy at the time, very clouds where no stars were visible and I viewed the phenomenon at exactly 9:43 pm. Eventually the lights faded into the clouds and disappeared. I was able to capture footage of the event on my Samsung galaxy s10e smartphone. I drew an image of the phenomenon on a screenshot of a map and my location, although I believe it was much farther away. Hope this helps!', 'posted': '2021-12-19T00:00:00', 'city_latitude': 36.35665012722647, 'city_longitude': -119.34793664122137}

 Example task return: INFO 2022-11-29 17:27:46,242 hooks 73706 8150787328 [('red', 'COLOR'), ('lights', 'TYPE'), ('red', 'COLOR'), ('lights', 'TYPE'), ('Lights', 'TYPE'), ('Demaree', 'GPE'), ('walnut', 'GPE'), ('visalia', 'GPE'), ('CA', 'GPE'), ('exactly 9:43 pm.', 'TIME'), ('lights', 'TYPE')]

"""

# function to get the data from the data source (CSV files)
def get_data(source=""):
    # if nuforc
    if source == settings.IE_SETTINGS["data_sources"]["nuforc"]:
        if (
            FIRST_RUN
        ):  # if first run, nothing to compare - it's all new, so load the lot
            data_dict = pd.read_csv(
                settings.IE_SETTINGS["data_sources"]["nuforc"]
            ).to_dict("records")
        else:
            # read data from CSV, only get changes from last time & put results in a dict
            new_data = compare(
                load_csv(
                    open(f'{settings.IE_SETTINGS["data_sources"]["nuforc-prev"]}'),
                    key="report_link",
                ),
                load_csv(
                    open(settings.IE_SETTINGS["data_sources"]["nuforc"]),
                    key="report_link",
                ),
            )
            data_dict = new_data["added"]
        # get raw text for each doc and put in a list
        doc_texts = get_text(data_dict)
        # get ents for each doc and put in a list
        doc_ents = extract_entities(doc_texts)
        # add extracted entities to the data dict
        data_with_ents = add_ents_to_data(data_dict, doc_ents)
        # return whatever to return for the final hook function (e.g., print to log, or write to DB unless that's done here - could be either ... return is sent to hooks as task.result)
        return data_with_ents
    elif source == settings.IE_SETTINGS["data_sources"]["reddit"]:
        pass


# function to extract the raw text from the data
def get_text(data_dict):
    doc_texts = []
    for doc in data_dict:
        doc_texts.append(doc["text"])
    return doc_texts


# function to run the NER on the document texts
def extract_entities(doc_texts):
    ner = Ner(
        model_name="trf-model-best-tuned",
        model_url="UFOzone/ner_models/trf-model-best-tuned/",
        doc_texts=doc_texts,
    )
    return ner.get_entities()

# function to add the extracted entities to the data
def add_ents_to_data(data_dict, doc_ents):
    for doc, ents in zip(data_dict, doc_ents):
        doc['entities'] = ents
    return data_dict
