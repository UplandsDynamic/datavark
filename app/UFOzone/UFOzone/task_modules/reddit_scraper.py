import logging
from datetime import datetime, timedelta
from django.conf import settings as s
import praw
from pmaw import PushshiftAPI
import pandas as pd

logger = logging.getLogger("django")


class RedditScraper:
    def __new__(cls, args=None, kwargs={}):
        obj = super().__new__(cls)
        return obj._get_data()

    def _get_data(self):
        _root_url = s.DA_SETTINGS["data_sources"]["reddit"]["source_root_url"]
        _praw_config = s.DA_SETTINGS["data_sources"]["reddit"]["praw_config"]
        reddit = praw.Reddit(
            client_id=_praw_config["praw_client_id"],
            client_secret=_praw_config["praw_client_secret"],
            username=_praw_config["praw_username"],
            password=_praw_config["praw_password"],
            user_agent=_praw_config["praw_user_agent"],
        )
        _data = []
        _api_praw = PushshiftAPI(praw=reddit)
        _start_epoch = int((datetime.today() - timedelta(days=7)).timestamp())
        """
        !Note: if changing "start_epoch", remember to also change "limit". Otherwise will still only get 7 days, as only the earliest 1 "submission" will be returned. E.g. 14 days in the timedelta function, requires a limit of at least 2 (equating to submission returns, which equals 2 weeks, as each "submission" under which its sighting report comments are posted is dedicated to 1 calendar week (as per the report submissions on the r/UFOs subreddit, here: https://www.reddit.com/r/UFOs/search?q=%22Weekly%20UFO%20Sightings%3A%22&restrict_sr=on&include_over_18=on&sort=new&t=all).
        """
        _submissions_search = _api_praw.search_submissions(
            title="Weekly UFO Sightings:", subreddit="ufos", limit=1, after=_start_epoch
        )
        for submission_found in _submissions_search:
            submission = reddit.submission(submission_found.get("id"))
            submission.comments.replace_more(limit=0)
            comments = submission.comments.list()
            for comment in comments:
                if comment.is_root:
                    _data.append(
                        {
                            "report_link": f"{_root_url}{comment.permalink}",
                            "text": comment.body,
                            "posted": datetime.fromtimestamp(
                                comment.created_utc
                            ).strftime("%Y-%m-%dT%H:%M:%S"),
                        }
                    )
        _df = pd.DataFrame(_data)
        _df.to_csv(s.DA_SETTINGS["data_sources"]["reddit"]["data_path"], index=False)
        return 1
