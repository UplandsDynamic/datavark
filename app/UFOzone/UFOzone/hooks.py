import logging
logger = logging.getLogger("django_q")



def print_result(task):
    # Get an instance of a logger
    logger.info(task.result)
