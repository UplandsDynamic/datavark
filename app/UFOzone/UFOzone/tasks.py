from django.conf import settings
import pandas as pd

def get_data(source=''):
    # if source == settings.IE_SETTINGS["data_sources"]["nuforc"]:
    #     data_dict = pd.read_csv(settings.IE_SETTINGS["data_sources"]["nuforc"]).to_dict("records")[0]
    #     return data_dict
    # elif source == settings.IE_SETTINGS["data_sources"]["reddit"]:
    #     pass
    return "Works!!!"