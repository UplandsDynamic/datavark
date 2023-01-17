import logging

logger = logging.getLogger("django_q")

def print_result(task):
    logger.info(f"Task result: {task.result}")
