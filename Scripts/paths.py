"""Shared path constants for the FRB-capstone pipeline."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
FIGURES = ROOT / "figures"
RESULTS = ROOT / "results"
SCRIPTS = ROOT / "Scripts"
NOTEBOOKS = ROOT / "Notebooks"
ARCHIVE = ROOT / "archive"
DATA_PACKAGE = ROOT / "Google_Drive_Data_Package"

GALAXIES = [
    "NGC_5846",
    "NGC_5576",
    "NGC_4623",
    "NGC_3245",
    "NGC_4762",
    "NGC_4378",
    "NGC_4814",
    "NGC_3938",
]


def galaxy_dir(galaxy: str) -> Path:
    return ROOT / f"{galaxy}_Analysis"


def galaxy_science(galaxy: str) -> Path:
    return galaxy_dir(galaxy) / "Science_Output"


def wsl_path(win_path: os.PathLike[str] | str) -> str:
    path = str(win_path)
    drive, rest = os.path.splitdrive(path)
    drive_letter = drive[0].lower()
    return f"/mnt/{drive_letter}{rest.replace(os.sep, '/')}"
