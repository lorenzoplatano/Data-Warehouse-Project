import json
import re
from pathlib import Path
from src.utils.geo_utils import normalize_geography

def extract_artist_name(creators_list):
    if not creators_list or not isinstance(creators_list, list):
        return "Unknown Artist"
    first_creator = creators_list[0]
    raw_desc = first_creator.get("description") or ""
    match = re.split(r"\(|\n", raw_desc)
    name = match[0].strip() if match else ""
    if not name or name.lower() in ["unknown", "anonymous", "unidentified"]:
        return "Unknown Artist"
    return name

def clean_cleveland_data():
    project_root = Path(__file__).resolve().parents[2]
    raw_path = project_root / "data" / "raw" / "cleveland_raw.json"
    processed_dir = project_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    output_path = processed_dir / "cleveland_cleaned.json"

    print("=== Starting data cleaning and normalization: Cleveland ===")

    with open(raw_path, "r", encoding="utf-8") as f:
        raw_records = json.load(f)

    cleaned_records = []

    for item in raw_records:
        source_id = str(item.get("id"))
        title = item.get("title")

        if not source_id or not title:
            continue

        height_cm, width_cm, area_cm2 = None, None, None
        dims = item.get("dimensions") or {}
        unframed = dims.get("unframed") or {}
        framed = dims.get("framed") or {}
        h_m = unframed.get("height") or framed.get("height")
        w_m = unframed.get("width") or framed.get("width")

        if h_m is not None and w_m is not None:
            try:
                h_float = float(h_m) * 100.0
                w_float = float(w_m) * 100.0
                if h_float > 0 and w_float > 0:
                    height_cm = round(h_float, 2)
                    width_cm = round(w_float, 2)
                    area_cm2 = round(height_cm * width_cm, 2)
            except (ValueError, TypeError):
                pass

        start_year = item.get("creation_date_earliest")
        end_year = item.get("creation_date_latest")
        try:
            start_year = int(start_year) if start_year is not None else None
        except (ValueError, TypeError):
            start_year = None
        try:
            end_year = int(end_year) if end_year is not None else None
        except (ValueError, TypeError):
            end_year = None


        if start_year is not None:
            if end_year is None or end_year <= 0 or end_year < start_year:
                end_year = start_year

        production_duration = max(0, end_year - start_year) if (start_year is not None and end_year is not None) else None
        artist_name = extract_artist_name(item.get("creators"))
        medium_raw = item.get("technique")

        culture_field = item.get("culture")
        place_raw = None
        if isinstance(culture_field, list) and len(culture_field) > 0:
            place_raw = culture_field[0]
        elif isinstance(culture_field, str):
            place_raw = culture_field

        geo_info = normalize_geography(place_raw)

        cleaned_records.append({
            "museum_name": "Cleveland Museum of Art",
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

    print(f"Cleveland cleaning complete! {len(cleaned_records)} paintings normalized and saved.")

if __name__ == "__main__":
    clean_cleveland_data()