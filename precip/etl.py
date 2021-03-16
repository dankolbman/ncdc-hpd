"""
Contains the ETL class that has functions for different stages of the data
pipeline.
"""
import os
import logging
import pandas as pd

from precip.config import Config
from precip.enums import StateEnum
from precip.reader import read_hpd
from precip.download import download_state, extract_data, combine_data
from precip.transform import was_deleted
from precip.analysis import (
    monthly_precip,
    active_stations,
    average_yearly_by_station,
)

logger = logging.getLogger(__name__)


class StateETL:
    """
    Captures different steps for an ETL of an HPD dataset for a given state.
    """

    def __init__(self, state: StateEnum):
        self.state = state

        # These are common paths that will be used to store files for
        # different operations in the pipeline
        self.combined_path = os.path.join(
            Config.DATA_DIR, f"{self.state.value:02}", "combined.txt"
        )
        self.transformed_path = os.path.join(
            Config.DATA_DIR, f"{self.state.value:02}", "transformed.csv"
        )
        self.analysis_path = os.path.join(
            Config.DATA_DIR, f"{self.state.value:02}", "analysis"
        )

    def download(self) -> None:
        """
        The download 'pipeline' to download all data for this ETL's US state.
        This will download a full FTP directory of compressed tar archives
        then extract and combine them into one data file.
        """
        logger.info(f"Downloading data for US state '{self.state.name}'")
        download_state(state=self.state)
        logger.info(f"Extracting data for US state '{self.state.name}'")
        extract_data(state=self.state)
        logger.info(f"Combining data for US state '{self.state.name}'")
        combine_data(state=self.state)

    def transform(self) -> None:
        """
        Transforms a given HPD file into an easier to manage format.
        """
        logger.info("Transforming combined raw data into more managble format")

        # Make sure the required files are in place before trying to transform
        if not os.path.exists(self.combined_path):
            message = (
                f"No transformed data exists at {self.combined_path}. "
                "Perhaps the data has not yet been downloaded?"
            )
            logger.error(message)
            raise FileNotFoundError(message)

        df = read_hpd(self.combined_path)

        # Extract date into python native datetime and remove old columns
        df["date"] = pd.to_datetime(df[["Year", "Month", "Day"]])
        df = df.drop(columns=["Year", "Month", "Day"])

        # Make a new flag indicating if a record was deleted
        df["Was-Deleted"] = was_deleted(df)

        logger.info(f"Saving transformed data to {self.transformed_path}")
        df.to_csv(self.transformed_path)

    def analyze(self) -> None:
        """
        Run analysis on transformed files.
        """
        if not os.path.exists(self.transformed_path):
            message = (
                f"No transformed data exists at {self.transformed_path}. "
                "Perhaps the data has not yet been transformed?"
            )
            logger.error(message)
            raise FileNotFoundError(message)

        try:
            logger.debug(
                f"Making directory '{self.analysis_path} to store analysis in"
            )
            os.makedirs(self.analysis_path)
        except FileExistsError:
            logger.debug(f"Directory '{self.analysis_path}' already exists")

        df = pd.read_csv(
            self.transformed_path, index_col=0, parse_dates=["date"]
        )

        # All of the analysis requires data that was not deleted and is of
        # good quality so filter out .
        df = df[df["Was-Deleted"] == False]
        df = df[df["Data-Value"] != 99999]
        df = df[~df["FLAG1"].fillna("").str.contains("Q")]

        total_precip = df["Data-Value"].sum() / 100
        start_year = df["date"].min().year
        end_year = df["date"].max().year
        avg_precip = total_precip / (end_year - start_year)
        logger.info(
            f"Total precipitation collected from all stations from "
            f"{start_year} to {end_year}: "
            f"{total_precip} inches"
        )
        logger.info(
            f"That's an average of {avg_precip:.2f} inches collected per year"
        )

        monthly_precip(df, fig_path=self.analysis_path)
        active_stations(df, fig_path=self.analysis_path)
        average_yearly_by_station(df, fig_path=self.analysis_path)
        logger.info(f"Saved figures to {self.analysis_path}")
