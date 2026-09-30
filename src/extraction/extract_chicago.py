import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

BASE_URL = "https://api.artic.edu/api/v1/artworks"
PAGE_LIMIT = 100
MAX_WORKERS = 15  # Number of parallel requests

FIELDS = [
    "id", "title", "artist_title", "artist_display",
    "date_start", "date_end", "date_display",
    "medium_display", "place_of_origin",
    "dimensions_detail", "artwork_type_title", "classification_titles"
]

HEADERS = {"User-Agent": "MuseumDWHProject/1.0 (University Research)"}


def is_painting(item):
    art_type = (item.get("artwork_type_title") or "").strip().lower()
    classifications = [c.lower() for c in item.get("classification_titles") or []]
    return art_type == "painting" or "painting" in classifications


def fetch_page(page_num):
    params = {
        "page": page_num,
        "limit": PAGE_LIMIT,
        "fields": ",".join(FIELDS)
    }
    try:
        r = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            payload = r.json()
            data = payload.get("data", [])
            # Immediately filter for paintings only
            return [item for item in data if is_painting(item)]
    except Exception:
        pass
    return []


def extract_all_chicago_paintings():
    project_root = Path(__file__).resolve().parents[2]
    output_dir = project_root / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "chicago_raw.json"

    print("=== Starting parallel painting extraction: Chicago ===")

    # 1. Get the total number of pages
    r = requests.get(BASE_URL, params={"page": 1, "limit": PAGE_LIMIT}, headers=HEADERS, timeout=15)
    total_pages = r.json().get("pagination", {}).get("total_pages", 1332)
    print(f"Total catalog pages to scan: {total_pages}")

    paintings_dict = {}
    completed_pages = 0

    # 2. Run the multithreaded extraction
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_page = {executor.submit(fetch_page, p): p for p in range(1, total_pages + 1)}

        for future in as_completed(future_to_page):
            paintings = future.result()
            for p in paintings:
                paintings_dict[p["id"]] = p

            completed_pages += 1
            if completed_pages % 50 == 0 or completed_pages == total_pages:
                print(
                    f"Progress: {completed_pages}/{total_pages} pages processed | Unique paintings: {len(paintings_dict)}")

    lista_finale = list(paintings_dict.values())
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(lista_finale, f, ensure_ascii=False, indent=2)

    print(f"\nExtraction complete! Saved {len(lista_finale)} paintings to:\n{output_path}")


if __name__ == "__main__":
    extract_all_chicago_paintings()