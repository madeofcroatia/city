import pandas as pd


def get_df(data, min_date, max_date, modes, resolution, aggregation_method):
    #print(min_date, max_date)
    resampler = (
        data.set_index('date')[modes]
            .loc[min_date:max_date]
            .resample(resolution)
    )
    if aggregation_method == "mean":
        df = resampler.mean().reset_index()
    elif aggregation_method == "sum":
        df = resampler.sum().reset_index()
    
    return df

