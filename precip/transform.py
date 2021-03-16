"""
Different transformations for augmenting and formatting a raw HPD dataset.
"""
import pandas as pd
import numpy as np


def extract_date(df):
    """
    Condenses the Year, Month, and Date columns into a single date column
    of a native python DateTime type.
    Drops old date columns.

    Returns:
    """
    df["date"] = pd.to_datetime(df[["Year", "Month", "Day"]])
    return df


def was_deleted(df):
    """
    Constructs a new column to flag whether or not the data point was marked
    as deleted.

    Args:
        df - The pd.Dataframe to create flags for
    Returns:
        A pd.Series of True/False flags, True if the datapoint was deleted,
        False otherwise
    """
    deleted = pd.Series(False, index=df.index)
    starts = np.where(df["FLAG1"].str.contains("{").fillna(False))
    ends = np.where(df["FLAG1"].str.contains("}").fillna(False))
    for start, end in zip(starts[0], ends[0]):
        deleted.iloc[start:end] = True

    # Marks the last datapoint flagged with '}' as deleted but also any
    # single occurences where there is no starting or ending bracket
    deleted.iloc[starts] = True
    deleted.iloc[ends] = True

    return deleted


def is_missing(df):
    """
    Constructs a new column to flag whether or not the data point was marked
    as missing.

    Args:
        df - The pd.Dataframe to create flags for
    Returns:
        A pd.Series of True/False flags, True if the datapoint is missing,
        False otherwise
    """
    missing = pd.Series(False, index=df.index)
    starts = np.where(df["FLAG1"].str.contains(r"\[").fillna(False))
    ends = np.where(df["FLAG1"].str.contains(r"\]").fillna(False))
    for start, end in zip(starts[0], ends[0]):
        missing.iloc[start:end] = True

    # Marks the last datapoint flagged with ']' as missing but also any
    # single occurences where there is no starting or ending bracket
    missing.iloc[starts] = True
    missing.iloc[ends] = True

    return missing
