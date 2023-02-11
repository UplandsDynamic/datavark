import pandas as pd
import ast
from datetime import datetime
from geopy.geocoders import Nominatim

results = "exported_reddit_records_random.csv"
output_file = "reddit_extraction_evaluation.txt"
output = []
df = pd.read_csv(results, index_col="id")
d = df.to_dict("records")
for idx, record in enumerate(d, 1):
    dates = []
    times = []
    record_results = []
    resolved_coordinates = []
    # resolve coordinates to places
    geolocator = Nominatim(user_agent="UAP_Database")
    locs = ast.literal_eval(record["obs_locs"])
    for loc in locs:
        # note, format in reverse is (lat/long)!
        place = geolocator.reverse(
            (loc[1]["latitude"], loc[1]["longitude"]),
            exactly_one=False,
            addressdetails=True,
            zoom=None,
            namedetails=True,
        )
        resolved_coordinates.append(place)
    record_results.append(f"-.-.-.-.-.-.- {idx} -.-.-.-.-.-.-\n")
    record_results.append(f"Text: {record['obs_txt']}\n")
    record_results.append(f"Types: {record['obs_types']}\n")
    record_results.append(f"Colors: {record['obs_colors']}\n")
    record_results.append(f"Locs: {record['obs_locs']}\n")
    record_results.append(f"Resolved coordinates: {resolved_coordinates}\n")
    record_results.append(f"Dates: {record['obs_dates']}\n")
    record_results.append(f"Times: {record['obs_times']}\n")
    record_results.append("\n\n")
    output.append(record_results)

with open(output_file, 'w') as f:
    for o in output:
        f.write('\n'.join(o))