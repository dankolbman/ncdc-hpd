"""
Utility functions for reading an HPD formatted file.
"""
import pandas as pd


def read_hpd(path: str):
    """
    Read a Historical Precipitation Data file into a Pandas DataFrame and
    return it.

    See here for format spec:
    ftp://ftp.ncdc.noaa.gov/pub/data/hourly_precip-3240/dsi3240.pdf
    """
    cols = [
        "Record-Type",
        "State-Code",
        "Cooperative Network Index Number",
        "Cooperative Network Division Number",
        "Element-Type",
        "Element-Units",
        "Year",
        "Month",
        "Day",
        "Number-Reported-Values",
        "Time-Of-Value",
        "Data-Value",
        "FLAG1",
    ]
    colspecs = [
        (0, 3),
        (3, 5),
        (5, 9),
        (9, 11),
        (11, 15),
        (15, 17),
        (17, 21),
        (21, 23),
        (23, 27),
        (27, 30),
        (30, 34),
        (34, 40),
        (40, 42),
    ]
    return pd.read_fwf(path, names=cols, colspecs=colspecs, lowmem=True)
