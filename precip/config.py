"""
A configuration object for the ETL.
Contains general settings for source and target destination for data.
"""
from dataclasses import dataclass

@dataclass
class Config:
    """
    A config object can be overridden or inherited for different deployment
    environments.
    """
    DATA_DIR: str = "data"
    NOAA_FTP: str = "ftp.ncdc.noaa.gov"
    NOAA_FTP_ROOT_DIR : str = "/pub/data/hourly_precip-3240/"
