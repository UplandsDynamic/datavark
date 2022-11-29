import pandas as pd
from django.conf import settings
from .ner import Ner

def get_data(source=''):
    if source == settings.IE_SETTINGS["data_sources"]["nuforc"]:
        data_dict = pd.read_csv(settings.IE_SETTINGS["data_sources"]["nuforc"]).to_dict("records")[0]
        return extract_entities(data_dict)
    elif source == settings.IE_SETTINGS["data_sources"]["reddit"]:
        pass

"""
Example incoming NUFORC data:

 {'summary': 'Viewed some red lights in the sky appearing to be moving north and slower than an airplane.', 'city': 'Visalia', 'state': 'CA', 'date_time': '2021-12-15T21:45:00', 'shape': 'light', 'duration': '2 minutes', 'stats': 'Occurred : 12/15/2021 21:45  (Entered as : 12/15/2021 9:45 PM) Reported: 12/15/2021 10:30:54 PM 22:30 Posted: 12/19/2021 Location: Visalia, CA Shape: Light Duration:2 minutes', 'report_link': 'http://www.nuforc.org/webreports/165/S165881.html', 'text': 'Viewed some red lights in the sky appearing to be moving north and slower than an airplane. Saw multiple red lights moving in the sky in what appeared to be uniform motion, but could be wrong. Lights appeared to be traveling north or northwest slower than a plane. I viewed the phenomenon standing outside the planet fitness gym on Demaree and walnut in visalia CA, and I was facing west while filming them. The weather was cloudy at the time, very clouds where no stars were visible and I viewed the phenomenon at exactly 9:43 pm. Eventually the lights faded into the clouds and disappeared. I was able to capture footage of the event on my Samsung galaxy s10e smartphone. I drew an image of the phenomenon on a screenshot of a map and my location, although I believe it was much farther away. Hope this helps!', 'posted': '2021-12-19T00:00:00', 'city_latitude': 36.35665012722647, 'city_longitude': -119.34793664122137}

"""

def extract_entities(data_dict):
    ner = Ner(model_name='trf-model-best-tuned', model_url='UFOzone/ner_models/trf-model-best-tuned/', doc_texts=['I saw a disk hovering in the sky.'])  # replace with data from data dict ...
    return ner.get_entities()