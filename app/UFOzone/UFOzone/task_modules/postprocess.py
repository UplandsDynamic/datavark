import datetime, dateutil, re, logging, string
from django.contrib.gis.geos import Point
from django.conf import settings
from dateutil.parser import ParserError
from .color_factory import ColorFactory
from geopy.geocoders import Nominatim

logger = logging.getLogger("django")


class PostProcess:

    """
    Processes the data to produce standardised input for the model fields
    """

    def __new__(cls, data=[], source=""):
        obj = super().__new__(cls)
        obj._data = data
        obj._source = source
        return obj._process()

    def _process(self):
        _processed_docs = []
        # NUFORC
        if self._source == settings.DA_SETTINGS["data_sources"]["nuforc"]:
            logger.info("Running post-processing for NUFORC data.")
            for doc in self._data:  # for every document
                _processed_docs.append(
                    {
                        "source_name": settings.DA_SETTINGS["data_sources"]["nuforc"][
                            "source_name"
                        ],
                        "source_url": self._process_source_url(doc["report_link"]),
                        "obs_txt": self._process_text(doc["text"]),
                        "obs_types": self._process_types(
                            # to txt NER also adds 'shape' as defined in structured NUFORC data
                            [e[0] for e in doc["entities"] if e[1] == "TYPE"]
                            + [doc["shape"]]
                        ),
                        "obs_colors": self._process_colors(
                            [e[0] for e in doc["entities"] if e[1] == "COLOR"]
                        ),
                        "obs_dates": self._process_dates([doc["date_time"]])[0],
                        "obs_times": self._process_times([doc["date_time"]])[0],
                        "obs_locs": self._process_locs(
                            [
                                [
                                    doc["city"],
                                    doc["state"],
                                    float(doc["city_longitude"])
                                    if doc["city_longitude"]
                                    else float(0),
                                    float(doc["city_latitude"])
                                    if doc["city_latitude"]
                                    else float(0),
                                ]
                            ]
                        ),
                    }
                )
        # REDDIT
        elif self._source == settings.DA_SETTINGS["data_sources"]["reddit"]:
            logger.info("Preprocessing for Reddit data")
            for doc in self._data:  # for every document
                doc = self._geocode(doc)  # add long/lat to GPE & LOC entity tuples
                _processed_docs.append(
                    {
                        "source_name": settings.DA_SETTINGS["data_sources"]["reddit"][
                            "source_name"
                        ],
                        "source_url": self._process_source_url(doc["report_link"]),
                        "obs_txt": self._process_text(doc["text"]),
                        "obs_types": self._process_types(
                            # to txt NER also adds 'shape' as defined in structured NUFORC data
                            [e[0] for e in doc["entities"] if e[1] == "TYPE"]
                        ),
                        "obs_colors": self._process_colors(
                            [e[0] for e in doc["entities"] if e[1] == "COLOR"]
                        ),
                        "obs_dates": self._process_dates(
                            [e[0] for e in doc["entities"] if e[1] == "DATE"]
                        )[0],
                        "obs_times": self._process_times(
                            [e[0] for e in doc["entities"] if e[1] == "TIME"]
                        )[0],
                        "obs_locs": self._process_locs(
                            [  # required empty 'state' list, as not distinguished in GPE from unstructured NER
                                [
                                    e[0],
                                    [],
                                    float(e[2]) if e[2] else float(0),
                                    float(e[3]) if e[3] else float(0),
                                ]
                                for e in doc["entities"]
                                if e[1] in ["GPE", "LOC"]
                            ]
                        ),
                    }
                )
        return _processed_docs

    # process observation types
    def _process_colors(self, colors=[]):
        formatted = []
        for color in colors:
            s = Scrubbers(color)
            color = s.run_color_scrubbers()
            if color:
                formatted.append(color)
        return list(set(formatted))

    # process observation types
    def _process_types(self, types=[]):
        formatted = []
        for type in types:
            s = Scrubbers(type)
            type = s.run_type_scrubbers()
            formatted.append(type)
        return list(set(formatted))

    # geocode locations with longitude & latitude
    def _geocode(self, doc):
        for idx, entity in enumerate(doc["entities"]):
            if entity[1] in ["GPE", "LOC"]:
                try:
                    geolocator = Nominatim(user_agent="UAP_Database")
                    location = geolocator.geocode(entity[0])
                    doc["entities"][idx] = (
                        entity[0],
                        entity[1],
                        location.longitude,
                        location.latitude,
                    )
                except Exception as e:
                    logger.error(
                        f"A problem occurred during geocoding - entity {idx} has NOT been geocoded!: {str(e)}"
                    )
        return doc

    # process place name. Returns list [{"place name": "name string", "coordinates": Point(longitude,latitude)})]
    def _process_locs(self, locs=[]):
        formatted = []
        for loc in locs:
            formatted.append(
                {
                    "place_name": f"{loc[0]}, {loc[1] if loc[1] else ''}".rstrip(", "),
                    "coordinates": Point(loc[2], loc[3])
                    if loc[2] and loc[3]
                    else Point(0, 0),
                }
            ) if Point(loc[2], loc[3]) not in [
                f["coordinates"] for f in formatted
            ] else None
        return formatted

    # process date from strings & return list of datetime.date objects
    def _process_dates(self, date_strings=[]):
        formatted = []
        discarded = []
        for date in date_strings:
            try:
                parsed = dateutil.parser.parse(date, fuzzy=True).date()
                formatted.append(parsed)
            except ParserError:
                discarded.append(date)
        return list(set(formatted)), discarded

    # process time from strings & return list of datetime.time objects
    def _process_times(self, time_strings=[]):
        duration_indicators = ["MINUTES", "MIN", "MINS", "M" "HOURS", "HRS", "HRS", "H"]
        formatted = []
        discarded = []  # likely durations. Not needed, but grab for possible future dev
        for time in time_strings:
            if any(i in time.upper().split() for i in duration_indicators):
                discarded.append(time)
            else:
                try:
                    # substitute dots for colons so time's recognised by parser
                    time = re.sub(r"(\d{1,2})\.(\d{2})(\D*)$", r"\1:\2\3", time)
                    # do some light string operations (regex) to detect semantic equivalences
                    time = re.sub(r"half past (\d).*morning", r"\1:30am", time)
                    time = re.sub(r"half past (\d).*afternoon", r"\1:pm", time)
                    time = re.sub(r"half\s{0,3}(\d).*morning", r"\1:30am", time)
                    time = re.sub(r"half\s{0,3}(\d).*afternoon", r"\1:30pm", time)
                    parsed = dateutil.parser.parse(time, fuzzy=True).time()
                    formatted.append(parsed) if parsed != datetime.time(0, 0) else None
                except ParserError:
                    discarded.append(time)
        return list(set(formatted)), discarded

    # process source URL
    def _process_source_url(self, url=""):
        # do any URL processing here, if required
        return url

    # process raw text account
    def _process_text(self, text=""):
        # do any string processing here, if required
        return text


class Scrubbers:
    def __init__(self, input):
        self.input = input

    def run_color_scrubbers(self):
        self._remove_whitespace()
        self._capitalize()
        self._remove_nonalphanumeric()
        self._remove_single_chars()
        self._standardise_color()
        return self.input

    def run_type_scrubbers(self):
        self._remove_whitespace()
        self._capitalize()
        self._remove_nonalphanumeric()
        self._remove_single_chars()
        self._standardise_light()
        self._standardise_tictac()
        self._standardise_orb()
        self._standardise_fireball()
        self._standardise_triangle()
        self._standardise_rectangle()
        self._standardise_disk()
        self._standardise_circle()
        self._standardise_cigar()
        self._standardise_misc()
        self._remove_whitespace()
        return self.input

    # function to standardise colours
    def _standardise_color(self):
        extended_endings = ["ISH", "EY", "Y"]
        filtered = filter(
            lambda c: c in ColorFactory(endings=extended_endings), self.input.split()
        )
        self.input = " ".join(filtered)

    # function to remove the appended word "shaped"
    def _remove_shaped(self):
        self.input = re.sub(re.sub(r"\bSHAPED.*\b", "", self.input))

    # function to remote whitespace leading/trailing whitespace
    def _remove_whitespace(self):
        self.input = self.input.strip()

    # function to capitalize
    def _capitalize(self):
        self.input = self.input.upper()

    # function to remove non-alphanumeric characters (preserve whitespace, replace with space)
    def _remove_nonalphanumeric(self):
        self.input = re.sub(r"[^\w\s]", " ", self.input)

    # function to remove strings with single char
    def _remove_single_chars(self):
        self.input = "" if len(self.input) <= 1 else self.input

    # function to change standardise 'light'
    def _standardise_light(self):
        self.input = re.sub(r"\b.*LIGHT.*\b", "LIGHT", self.input)
        self.input = re.sub(r"\bDOT.*\b", "LIGHT", self.input)
        self.input = re.sub(r"\bSTAR.*\b", "LIGHT", self.input)
        self.input = re.sub(r"\bFLASH.*\b", "LIGHT", self.input)
        self.input = re.sub(r"\b.*STREAK\b", "LIGHT", self.input)
        self.input = re.sub(r"\b.*GLOW.*\b", "LIGHT", self.input)
        self.input = re.sub(r"\b.*PIN\s*PRICK.*\b", "LIGHT", self.input)
        self.input = re.sub(r"\b.*STROBE.*\b", "LIGHT", self.input)
        self.input = re.sub(r"\b.*TWINKLE.*\b", "LIGHT", self.input)

    # function to change standardise 'fireball'
    def _standardise_fireball(self):
        self.input = re.sub(r"\b.*FIREBALL.*\b", "FIREBALL", self.input)

    # function to change standardise 'orb'
    def _standardise_orb(self):
        self.input = re.sub(r"\b.*\s*ORB.*\b", "ORB", self.input)
        self.input = re.sub(r"\b.*ROUND\s*ORB.*\b", "ORB", self.input)
        self.input = re.sub(r"\bBALL.*\b", "ORB", self.input)

    # function to change standardise 'tic tac'.
    def _standardise_tictac(self):
        self.input = re.sub(r"\b.*TICT.*\b", "TIC TAC", self.input)
        self.input = re.sub(r"\b.*TIKT.*\b", "TIC TAC", self.input)
        self.input = re.sub(r"\b.*TIC T.*\b", "TIC TAC", self.input)

    # function to change standardise variations of 'triangle'.
    def _standardise_triangle(self):
        self.input = re.sub(r"\b.*RIANG.*\b", "TRIANGLE", self.input)

    # function to change standardise variations of 'rectangle'.
    def _standardise_rectangle(self):
        self.input = re.sub(r"\b.*RECTANG.*\b", "RECTANGLE", self.input)

    # function to change standardise variations of 'disk'.
    def _standardise_disk(self):
        self.input = re.sub(r"\b.*DISC.*\b", "DISK", self.input)
        self.input = re.sub(r"\b.*DISK.*\b", "DISK", self.input)
        self.input = re.sub(r"\b.*SAUCER.*\b", "SAUCER", self.input)

    # function to change standardise variations of 'circle'.
    def _standardise_circle(self):
        self.input = re.sub(r"\bCIRC.*\b", "CIRCLE", self.input)

    # function to change standardise variations of 'cigar'.
    def _standardise_cigar(self):
        self.input = re.sub(r"\bCIGAR.*\b", "CIGAR", self.input)

    # function to change standardise miscellaneous misfits'.
    def _standardise_misc(self):
        self.input = re.sub(r"\bUNKNOWN\b", "OTHER", self.input)
        self.input = re.sub(r"\bOBJECT.*\b", "OTHER", self.input)
        self.input = re.sub(r"\bUFO.*\b", "OTHER", self.input)
