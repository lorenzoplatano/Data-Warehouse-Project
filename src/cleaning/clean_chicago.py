import json
import re
from pathlib import Path
from src.utils.geo_utils import normalize_geography


def clean_chicago_data():
    project_root = Path(__file__).resolve().parents[2]
    raw_path = project_root / "data" / "raw" / "chicago_raw.json"
    processed_dir = project_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    output_path = processed_dir / "chicago_cleaned.json"

    print("=== Starting data cleaning and normalization: Chicago ===")

    with open(raw_path, "r", encoding="utf-8") as f:
        raw_records = json.load(f)

    cleaned_records = []

    for item in raw_records:
        source_id = str(item.get("id"))
        title = item.get("title")

        if not source_id or not title:
            continue

        height_cm, width_cm, area_cm2 = None, None, None
        dims_detail = item.get("dimensions_detail")
        if dims_detail and isinstance(dims_detail, list) and len(dims_detail) > 0:
            first_dim = dims_detail[0]
            h = first_dim.get("height")
            w = first_dim.get("width")
            if h is not None and w is not None:
                try:
                    height_cm = round(float(h), 2)
                    width_cm = round(float(w), 2)
                    if height_cm > 0 and width_cm > 0:
                        area_cm2 = round(height_cm * width_cm, 2)
                except (ValueError, TypeError):
                    pass

        start_year = item.get("date_start")
        end_year = item.get("date_end")
        try:
            start_year = int(start_year) if start_year is not None else None
        except (ValueError, TypeError):
            start_year = None
        try:
            end_year = int(end_year) if end_year is not None else None
        except (ValueError, TypeError):
            end_year = None

        production_duration = max(0, end_year - start_year) if (start_year is not None and end_year is not None) else None

        artist_name = item.get("artist_title")
        if not artist_name:
            raw_display = item.get("artist_display") or ""
            match = re.split(r"\(|\n", raw_display)
            artist_name = match[0].strip() if match else None

        if not artist_name or artist_name.lower() in ["unknown", "anonymous", "unidentified"]:
            artist_name = "Unknown Artist"

        medium_raw = item.get("medium_display")
        place_raw = item.get("place_of_origin")

        geo_info = normalize_geography(place_raw)

        cleaned_records.append({
            "museum_name": "Art Institute of Chicago",
            "source_id": source_id,
            "title": title.strip(),
            "artist_name": artist_name,
            "start_year": start_year,
            "end_year": end_year,
            "production_duration": production_duration,
            "height_cm": height_cm,
            "width_cm": width_cm,
            "area_cm2": area_cm2,
            "medium_raw": medium_raw.strip() if medium_raw else None,
            "place_raw": geo_info["country"],
            "macro_region": geo_info["macro_region"],
            "continent": geo_info["continent"]
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_records, f, ensure_ascii=False, indent=2)

    print(f"Chicago cleaning complete! {len(cleaned_records)} paintings normalized and saved.")


if __name__ == "__main__":
    clean_chicago_data()