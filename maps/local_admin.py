import os
from datetime import datetime
from glob import glob
from pathlib import Path

from django.utils.timezone import make_aware

from .models import Map


def ingest_map(dirpath: Path, map_id: str):
    jpg_path = dirpath / f"{map_id}.jpg"
    yrd_path = dirpath / f"{map_id}.yrd"
    his_path = dirpath / f"{map_id}.his"

    date_str = ""

    with open(yrd_path) as f:
        for line in f:
            if line.startswith("Fver="):
                date_str = line.split("=")[1].strip()
                break

    if not date_str:
        raise ValueError(f"Could not find Fver line in {yrd_path}")

    date = make_aware(datetime.strptime(date_str, r"%m/%d/%Y"))

    m = Map(
        id=map_id,
        modified_date=date,
        jpg_file=jpg_path,
        yrd_file=yrd_path,
        his_file=his_path,
    )
    m.save()


def ingest_all(dirpath: Path):
    for yrd_file in glob(str(dirpath / "*.yrd")):
        map_id = os.path.splitext(os.path.basename(yrd_file))[0]
        ingest_map(dirpath, map_id)
