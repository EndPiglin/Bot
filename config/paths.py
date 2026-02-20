from pathlib import Path


class Paths:
    def __init__(self):
        self.root = Path(__file__).resolve().parent.parent
        self.data_dir = self.root / "data"
        self.streams_dir = self.data_dir / "streams"
        self.daily_dir = self.data_dir / "daily"
        self.config_file = self.data_dir / "config.json"

        self.data_dir.mkdir(exist_ok=True)
        self.streams_dir.mkdir(exist_ok=True)
        self.daily_dir.mkdir(exist_ok=True)
