import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def load_json(filename: str):
    filepath = DATA_DIR / filename
    try:
        with filepath.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Файл данных не найден: {filepath}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Ошибка разбора JSON в файле {filepath}: {exc}") from exc


def load_content():
    return load_json("content.json")


def load_hackathons():
    return load_json("hackathons.json")


def load_startups():
    return load_json("startups.json")
