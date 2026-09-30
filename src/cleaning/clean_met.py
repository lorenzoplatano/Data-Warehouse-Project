import json
import re
from pathlib import Path
from src.utils.geo_utils import normalize_geography

PAINTING_KEYWORDS = ["oil", "canvas", "panel", "wood", "tempera", "watercolor", "acrylic", "fresco", "distemper",
                     "gouache", "linen", "paper", "board", "masonite", "encaustic"]
EXCLUDE_KEYWORDS = ["snuffbox", "porcelain", "plaque", "medallion", "silver", "gold", "ceramic", "sculpture", "statue",
                    "glass", "metal", "copper plate"]


def is_true_painting(title, medium):
    text = f"{title or ''} {medium or ''}".lower()
    if any(bad_kw in text for bad_kw in EXCLUDE_KEYWORDS):
        if not ("oil" in text or "tempera" in text):
            return False
    return any(kw in text for kw in PAINTING_KEYWORDS)


def parse_met_dimensions(dim_str):
    if not dim_str or not isinstance(dim_str, str):
        return None, None, None

    match_rect = re.search(r"\(\s*([\d\.]+)\s*(?:x|×)\s*([\d\.]+)\s*(?:x\s*[\d\.]+\s*)?cm\)", dim_str, re.IGNORECASE)
    if match_rect:
        try:
            h, w = float(match_rect.group(1)), float(match_rect.group(2))
            if h > 0 and w > 0:
                return round(h, 2), round(w, 2), round(h * w, 2)
        except ValueError:
            pass

    match_diam = re.search(r"(?:diam\.|diameter)[^\(]*\(\s*([\d\.]+)\s*cm\)", dim_str, re.IGNORECASE)
    if match_diam:
        try:
            d = float(match_diam.group(1))
            if d > 0:
                return round(d, 2), round(d, 2), round(d * d, 2)
        except ValueError:
            pass

    match_inch = re.search(r"([\d\.\s/]+)\s*(?:x|×)\s*([\d\.\s/]+)\s*in\.", dim_str, re.IGNORECASE)
    if match_inch:
        try:
            def to_float(val_str):
                parts = val_str.strip().split()
                total = 0.0
                for p in parts:
                    if "/" in p:
                        num, den = p.split("/")
                        total += float(num) / float(den)
                    else:
                        total += float(p)
                return total

            h = to_float(match_inch.group(1)) * 2.54
            w = to_float(match_inch.group(2)) * 2.54
            if h > 0 and w > 0:
                return round(h, 2), round(w, 2), round(h * w, 2)
        except Exception:
            pass

    return None, None, None


def clean_met_data():
    project_root = Path(__file__).resolve().parents[2]
    raw_path = project_root / "data" / "raw" / "met_raw.json"
    processed_dir = project_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    output_path = processed_dir / "met_cleaned.json"

    print("=== Starting data cleaning and normalization: The Met ===")

    with open(raw_path, "r", encoding="utf-8") as f:
        raw_records = json.load(f)

    cleaned_records = []
    filtered_out_count = 0

    for item in raw_records:
        source_id = str(item.get("objectID") or "")
        title = item.get("title")
        medium_raw = item.get("medium")

        if not source_id or not title:
            continue

        if not is_true_painting(title, medium_raw):
            filtered_out_count += 1
            continue

        height_cm, width_cm, area_cm2 = parse_met_dimensions(item.get("dimensions"))

        start_year = item.get("objectBeginDate")
        end_year = item.get("objectEndDate")
        try:
            start_year = int(start_year) if start_year is not None else None
        except (ValueError, TypeError):
            start_year = None
        try:
            end_year = int(end_year) if end_year is not None else None
        except (ValueError, TypeError):
            end_year = None

        production_duration = max(0, end_year - start_year) if (start_year is not None and end_year is not None) else None

        artist_name = item.get("artistDisplayName")
        if artist_name:
            artist_name = artist_name.split("|")[0].strip()
        if not artist_name or artist_name.lower() in ["unknown", "anonymous", "unidentified", ""]:
            artist_name = "Unknown Artist"

        country = item.get("country")
        culture = item.get("culture")
        place_raw = country or culture
        if place_raw:
            place_raw = place_raw.split("|")[0].strip()

        geo_info = normalize_geography(place_raw)

        cleaned_records.append({
            "museum_name": "The Metropolitan Museum of Art",
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

    print(f"Met cleaning complete! {len(cleaned_records)} paintings normalized and saved.")


if __name__ == "__main__":
    clean_met_data()