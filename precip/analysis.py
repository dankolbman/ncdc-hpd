"""
Various analysis functions to run on a cleaned and transformed dataset.
These will often produce figures at specified paths.
"""
import os
import pandas as pd
from matplotlib import pyplot as plt


def monthly_precip(df: pd.DataFrame, fig_path: str):
    """
    Calculate the total amount of precipitation collected and bin by month.
    Note that this is just precipitation collected an not necessarily
    indicative of precipitation that occurred during a month in any given
    region.
    """
    f = plt.figure(figsize=(16, 4))
    (
        df.groupby(pd.Grouper(key="date", freq="1M"))["Data-Value"].sum() / 100
    ).plot()
    plt.title("Precipitation Collected Monthly")
    plt.ylabel("Precipitation (inches)")
    f.savefig(os.path.join(fig_path, "monthly_precip.png"))


def active_stations(df: pd.DataFrame, fig_path: str):
    """
    Plot number of reporting stations over yearly windows
    """
    f = plt.figure(figsize=(16, 4))
    df.groupby(pd.Grouper(key="date", freq="1Y"))[
        "Cooperative Network Index Number"
    ].nunique().plot()
    plt.title("Number of Yearly Active Stations")
    plt.ylabel("Number of Stations")
    f.savefig(os.path.join(fig_path, "active_stations.png"))


def avg_yearly_precip(df: pd.DataFrame, fig_path: str):
    """
    Plot average yearly precipitation over each station.
    """
    df_av = (
        df.groupby(
            [
                pd.Grouper(key="date", freq="1Y"),
                "Cooperative Network Index Number",
            ]
        )["Data-Value"]
        .sum()
        .reset_index()
        .groupby("date")
        .mean()
    )
    f = plt.figure(figsize=(16, 4))
    (df_av["Data-Value"] / 100).plot()
    plt.title("Average Yearly Precipitation")
    plt.ylabel("Precipitation (inches)")
    f.savefig(os.path.join(fig_path, "avg_yearly_precip.png"))


def average_yearly_by_station(df: pd.DataFrame, fig_path: str):
    """
    Plot average yearly precipitation by division.
    """
    # Normalize by number of active stations every year
    n = df.groupby(
        [
            "Cooperative Network Division Number",
            pd.Grouper(key="date", freq="1Y"),
        ]
    )["Cooperative Network Index Number"].nunique()
    n = n.reset_index().pivot(
        index="date", columns="Cooperative Network Division Number"
    )
    n = n[n.index > "1994"]

    n = n.droplevel(0, axis=1)
    n = n.drop(columns=[0])

    # Group by division and find total precipitation per year
    by_div = (
        df[df["Cooperative Network Division Number"] != 0]
        .groupby(
            [
                "Cooperative Network Division Number",
                pd.Grouper(key="date", freq="1Y"),
            ]
        )["Data-Value"]
        .sum()
        .reset_index()
        .pivot(
            index="date",
            columns="Cooperative Network Division Number",
            values="Data-Value",
        )
    )

    # Normalize the precipitation by division by number of stations and
    # convert to inches
    f = (by_div / n / 100).plot(figsize=(16, 4)).get_figure()
    plt.legend(title="Division", loc="upper left", ncol=8)
    plt.title("Average Yearly Precipitation by Division")
    plt.ylabel("Precipitation (inches)")
    f.savefig(os.path.join(fig_path, "average_yearly_by_station.png"))
