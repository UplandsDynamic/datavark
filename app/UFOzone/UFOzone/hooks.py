import logging

logger = logging.getLogger("django_q")

# call task_modules.db to write to db?

def print_result(task):
    # Get an instance of a logger
    logger.info(task.result)
