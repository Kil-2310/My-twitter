import os
from pathlib import Path

from dotenv import load_dotenv

find_dir = Path(__file__).parent.parent.parent
env_path = find_dir / ".env"

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    exit(f"Файл .env не найден по пути: {env_path}")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
