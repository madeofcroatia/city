import pandas as pd
import os

import os
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'relative/path/to/file/you/want')

print(filename)
ridership_df = pd.read_csv("data/cta-ridership-clean.csv", parse_dates=["date"])

def get_df(min_date, max_date, modes, resolution, aggregation_method, daytypes = ["U", "W", "A"]):
    #print(min_date, max_date)
    resampler = (
        ridership_df.query("day_type in @daytypes")
                    .set_index('date')[modes]
                    .loc[min_date:max_date]
                    .resample(resolution)
    )
    if aggregation_method == "mean":
        df = resampler.mean().reset_index()
    elif aggregation_method == "sum":
        df = resampler.sum().reset_index()
    
    return df

