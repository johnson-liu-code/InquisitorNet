from pathlib import Path
from phase1.config import Settings
from phase1.db import get_conn, migrate
from phase1.scraper import run_scraper_to_db
from phase1.detector import run_detector_to_db

BASE = Path(__file__).resolve().parents[1]

def main():
    settings = Settings(BASE)
    conn = get_conn(settings.database_path)
    migrate(conn, BASE/'migrations'/'001_init.sql')
    kept = run_scraper_to_db(settings, conn)
    marked, acquitted = run_detector_to_db(settings, conn)
    print(f"Scraper kept {kept} items. Detector → marked {marked}, acquitted {acquitted}. DB: {settings.database_path}")

if __name__ == "__main__":
    main()
