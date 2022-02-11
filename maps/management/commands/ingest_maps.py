import os
from datetime import datetime
from glob import glob
from pathlib import Path
from typing import cast

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware

from maps.models import Map


def ingest_map(dirpath: Path, map_id: int):
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

    date = make_aware(datetime.strptime(date_str, r"%d/%m/%Y"))

    if Map.objects.filter(pk=map_id).exists():
        m = cast(Map, Map.objects.get(pk=map_id))
        if m.modified_date == date:
            return
        m.modified_date = date

    else:
        m = Map(id=map_id, modified_date=date)

    with open(jpg_path, "rb") as f1:
        m.jpg_file.save(f"{map_id}.jpg", ContentFile(f1.read()))
    with open(yrd_path, "rb") as f2:
        m.yrd_file.save(f"{map_id}.yrd", ContentFile(f2.read()))
    with open(his_path, "rb") as f3:
        m.his_file.save(f"{map_id}.his", ContentFile(f3.read()))
    m.save()


def ingest_maps(dirpath: Path):
    for yrd_file in glob(str(dirpath / "*.yrd")):
        map_id = os.path.splitext(os.path.basename(yrd_file))[0]
        ingest_map(dirpath, int(map_id))


class Command(BaseCommand):
    help = "Ingests map data"

    def add_arguments(self, parser):
        parser.add_argument("dirpath", type=str)

    def handle(self, *args, **options):
        ingest_maps(Path(options["dirpath"]))
