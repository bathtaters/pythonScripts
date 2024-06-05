"""
------------------------------
Set File Modification from CSV
------------------------------
by bathtaters

CSV expects first two columns to be: filename, modified date/time
Modified Date/Time should be formatted: YYYYMMDDHHMM
"""

import csv, subprocess
from pathlib import Path

# Path appended to start of each filename
BASE_DIR = "/common/file/path/"

# CSV file path
CSV_PATH = Path(BASE_DIR, "dates.csv")

# CSV Column with filename (0-indexed)
COL_NAME = 0
# CSV Column with modification time (Format: YYYYMMDDHHMM, 0-indexed)
COL_DATE = 1

with open(CSV_PATH, 'r') as f:
    for row in csv.reader(f):
        name, date = row[COL_NAME], row[COL_DATE]
        print(f"Set '{name}' to {date[4:6]}/{date[6:8]}/{date[:4]} {date[8:10]}:{date[10:]}")
        subprocess.call(["touch", "-t", date, Path(BASE_DIR, name).as_posix()])