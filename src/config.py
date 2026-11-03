from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "instance" / "forensic_timeline.db"
SECRET_KEY = "change-this-development-key"
