import logging
logger = logging.getLogger('django')

def print_result(task):
    # Get an instance of a logger
    logger.info(task.result)
    
    # Schedule.objects.create(
    #     func='tasks.get_data',
    #     hook='hooks.print_result',
    #     args=("tester",),
    #     schedule_type=Schedule.MINUTES,
    #     minutes=minutes,
    #     repeats=repeats
    # )
    # args='/Users/dan/Dev/education/uhi/dissertation/finals/github_repo/app/UFOzone/nuforc/nuforc_reports.csv',