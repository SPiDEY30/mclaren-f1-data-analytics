from pathlib import Path
import re
import html
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "data" / "mclaren_race_data.csv"


def clean_column_name(value):
    """Normalize headers exported from CSV, Markdown, or HTML."""
    name = html.unescape(str(value)).strip()
    name = name.replace("\ufeff", "")
    name = re.sub(r"<[^>]*>", "", name)
    name = name.replace("**", "").replace("*", "")
    name = name.replace('"', "").replace("'", "").strip()
    name = name.replace(" ", "_")

    # Remove stray punctuation around column names.
    name = name.strip(" ,;")
    compact = re.sub(r"[^a-z0-9]", "", name.lower())

    aliases = {
        "season": "Season",
        "round": "Round",
        "date": "Date",
        "grandprix": "GrandPrix",
        "driver": "Driver",
        "racepos": "Race_Pos",
        "points": "Points",
        "finishposition": "Finish_Position",
        "podium": "Podium",
        "win": "Win",
        "cumulativepoints": "Cumulative_Points",
    }
    return aliases.get(compact, name)


def parse_bool(series):
    """Convert common true/false strings to actual Boolean values."""
    if series.dtype == bool:
        return series.fillna(False)

    normalized = series.astype(str).str.strip().str.lower()
    return normalized.map({
        "true": True, "false": False,
        "1": True, "0": False,
        "yes": True, "no": False,
        "y": True, "n": False,
    }).fillna(False).astype(bool)


def load_data():
    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"mclaren_race_data.csv was not found at: {CSV_FILE}"
        )

    df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
    df.columns = [clean_column_name(col) for col in df.columns]

    # If Win is absent, derive it from the classified finishing position.
    # Position 1 means a win; DNF/DNS/DSQ and blank positions are not wins.
    if "Win" not in df.columns:
        if "Finish_Position" in df.columns:
            finish = pd.to_numeric(df["Finish_Position"], errors="coerce")
            df["Win"] = finish.eq(1)
        else:
            raise ValueError(
                "CSV is missing both Win and Finish_Position, so wins "
                "cannot be determined. Check the CSV header row."
            )

    # If Podium is absent, derive it from finishing positions 1–3.
    if "Podium" not in df.columns:
        if "Finish_Position" in df.columns:
            finish = pd.to_numeric(df["Finish_Position"], errors="coerce")
            df["Podium"] = finish.between(1, 3)
        else:
            raise ValueError(
                "CSV is missing both Podium and Finish_Position, so podiums "
                "cannot be determined. Check the CSV header row."
            )

    required_columns = [
        "Season", "Round", "Date", "GrandPrix", "Driver",
        "Race_Pos", "Points", "Finish_Position", "Podium", "Win",
        "Cumulative_Points",
    ]
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(
            "CSV is missing required columns: " + ", ".join(missing)
            + ". Check the CSV header row."
        )

    numeric_columns = [
        "Season", "Round", "Race_Pos", "Points",
        "Finish_Position", "Cumulative_Points",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Podium"] = parse_bool(df["Podium"])
    df["Win"] = parse_bool(df["Win"])

    return df
