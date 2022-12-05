import dummy_data
from django.conf import settings
import logging
from UFOzone.task_modules.db import WriteToDB
from UFOzone.task_modules.postprocess import PostProcess

logger = logging.getLogger("django")


def test():
    # test writing to model (remove all this and uncomment self.set_data_scan above when done)

    dummy_sources = {
        "reddit": {
            "source": settings.DA_SETTINGS["data_sources"]["reddit"],
            "data": dummy_data.DUMMY_REDDIT,
        },
        "nuforc": {
            "source": settings.DA_SETTINGS["data_sources"]["nuforc"],
            "data": dummy_data.DUMMY_NUFORC,
        },
    }
    data = PostProcess(
        data=dummy_sources[settings.DA_SETTINGS["test_source"]]["data"],
        source=dummy_sources[settings.DA_SETTINGS["test_source"]]["source"],
    )
    result = WriteToDB(data=data)
    logger.info(result)
