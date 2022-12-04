DUMMY_NUFORC = [
    {
        "summary": "Summary of observation",
        "city": "New York City",
        "state": "NY",
        "date_time": "2021-12-15T21:45:00",
        "shape": "light",
        "duration": "2 minutes",
        "stats": "Occurred : 12/15/2021 21:45  (Entered as : 12/15/2021 9:45 PM) Reported: 12/15/2021 10:30:54 PM 22:30 Posted: 12/19/2021 Location: New York City, NY Shape: Light Duration:2 minutes",
        "report_link": "http://www.nuforc.org/webreports/382/S165832.html",
        "text": "Description of observation.",
        "posted": "2021-12-19T00:00:00",
        "city_latitude": 36.35665012722647,
        "city_longitude": -119.34793664122137,
        # "city_latitude": "",  # test with no fields submitted for lat/long
        # "city_longitude": "",
        "entities": [
            ("red", "COLOR"),
            ("bluey", "COLOR"),
            ("redy green", "COLOR"),
            ("lights!", "TYPE"),
            ("lights!", "TYPE"),
            ("New York City", "GPE"),
            ("NY", "GPE"),
        ],
    }
]

DUMMY_REDDIT = [
    {
        "report_link": "https://www.reddit.com/r/UFOs/comments/z5wc7d/weekly_ufo_sightings_november_27_december_03_2022/",
        "text": "Description of observation.",
        "posted": "2023-02-19T00:00:00",
        "entities": [
            ("red", "COLOR"),
            ("lights", "TYPE"),
            ("l", "TYPE"),
            ("New York City", "GPE", -119.34793664122137,36.35665012722647),# name, ent type, longitude, latitude
            ("New York City", "GPE", -119.34793664122137,36.35665012722647),  
            ("NY", "GPE", -119.34793664122137,36.35665012722647),
            ("230 pm", "TIME"),
            ("10 September", "DATE"),
        ],
    }
]
