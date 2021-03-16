"""
Loads NOAA precipitation data from their ftp server into memory.
"""
import os
import logging
from ftplib import FTP
from subprocess import Popen

from precip.enums import StateEnum
from precip.config import Config


logger = logging.getLogger(__name__)


def download_state(state: StateEnum) -> None:
    """
    Downloads data for a given state to the data directory.
    Data will be saved into a folder specific to the state and within a raw/
    folder.
    """
    download_dir = os.path.join(Config.DATA_DIR, f"{state.value:02}", "raw")
    try:
        logger.debug(f"Making directory '{download_dir} to download files to")
        os.makedirs(download_dir)
    except FileExistsError:
        logger.debug(f"Directory '{download_dir}' already exists")

    try:
        ftp = FTP(Config.NOAA_FTP)
        ftp.login()
        ftp.cwd(os.path.join(Config.NOAA_FTP_ROOT_DIR, f"{state.value:02}"))
    except Exception:
        logger.error(
            "There was an error trying to communicate with the FTP server"
        )
        raise

    for i, filename in enumerate(ftp.nlst()):
        logger.debug(f"Downloading datafile: {filename}")
        out_path = os.path.join(
            Config.DATA_DIR, f"{state.value:02}", "raw", filename
        )
        if os.path.exists(out_path):
            logger.debug(
                f"File at path '{out_path}' already exists, "
                "will skip downloading"
            )
            continue
        with open(out_path, "wb") as f:
            ftp.retrbinary("RETR " + filename, f.write)

    ftp.quit()

    logger.info(f"Downloaded {i} data files for '{state.name}'")


def extract_data(state: StateEnum) -> None:
    """
    Extracts data from the raw/ directory into an extracted/ directory

    There is no python library to handle the ancient Unix archive format
    so we resort to extracting it inside another process using zcat.
    """
    raw_path = os.path.join(Config.DATA_DIR, f"{state.value:02}", "raw")
    extract_path = os.path.join(
        Config.DATA_DIR, f"{state.value:02}", "extracted"
    )
    try:
        os.makedirs(extract_path)
    except FileExistsError:
        logger.debug(f"Directory '{extract_path}' already exists")
    logger.debug(f"Extracting data in {raw_path} to {extract_path}")
    files = os.listdir(raw_path)
    for f in files:
        logger.debug(f"Extracting {f}")
        Popen(
            f"zcat ./{raw_path}/{f} | tar -xvf - -C ./{extract_path}",
            shell=True,
            stdout=open(os.devnull, "w"),
            stderr=open(os.devnull, "w"),
        )


def combine_data(state: StateEnum) -> None:
    """
    Extracts data from the raw/ directory into an extracted/ directory

    There is no python library to handle the ancient Unix archive format
    so we resort to extracting it inside another process using zcat.
    """
    extract_path = os.path.join(
        Config.DATA_DIR, f"{state.value:02}", "extracted"
    )
    combine_path = os.path.join(
        Config.DATA_DIR, f"{state.value:02}", "combined.txt"
    )
    logger.debug(f"Combining data in {extract_path} to {combine_path}")
    try:
        os.remove(combine_path)
    except FileNotFoundError:
        pass

    Popen(
        f"cat {extract_path}/* >> {combine_path}",
        shell=True,
        stdout=open(os.devnull, "w"),
        stderr=open(os.devnull, "w"),
    )

    logger.info(
        f"Combined all data for US state '{state.name}' to  {combine_path}"
    )
