import os
from glob import glob
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from tqdm import tqdm

from trains.models import Train


def ingest_train(filepath: Path):
    filename = filepath.name

    tokens = os.path.splitext(filename)[0].split("-")
    to_player = tokens[3]
    from_player = tokens[4]

    train_obj = Train.objects.create(
        to_player=to_player,
        from_player=from_player,
    )
    with open(filepath, "rb") as f:
        train_obj.train_file.save(filename, ContentFile(f.read()))


def ingest_maps(dirpath: Path):
    for train_file in tqdm(glob(str(dirpath / "Y*.zr*"))):
        ingest_train(Path(train_file))


class Command(BaseCommand):
    help = "Ingests train data"

    def add_arguments(self, parser):
        parser.add_argument("dirpath", type=str)

    def handle(self, *args, **options):
        ingest_maps(Path(options["dirpath"]))
