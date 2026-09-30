import json
import time
from pathlib import Path
import requests

BASE_URL = "https://openaccess-api.clevelandart.org/api/artworks/"
PAGE_LIMIT = 100  # Recommended maximum per request

HEADERS = {"User-Agent": "MuseumDWHProject/1.0 (University Research)"}


def extract_all_cleveland_paintings():
  # Path to the data/raw directory
  project_root = Path(__file__).resolve().parents[2]
  output_dir = project_root / "data" / "raw"
  output_dir.mkdir(parents=True, exist_ok=True)
  output_path = output_dir / "cleveland_raw.json"

  paintings = []
  skip = 0
  total_paintings = None

  print("=== Starting complete painting extraction: Cleveland ===")

  while True:
    params = {
        "type": "Painting",
        "limit": PAGE_LIMIT,
        "skip": skip,
    }

    try:
      response = requests.get(
          BASE_URL, params=params, headers=HEADERS, timeout=20
      )
      response.raise_for_status()
      payload = response.json()

      if total_paintings is None:
        total_paintings = payload.get("info", {}).get("total", 0)
        print(f"Total paintings to download: {total_paintings}")

      records = payload.get("data", [])
      if not records:
        print("No more records returned. Scan complete.")
        break

      paintings.extend(records)
      print(
          f"Offset {skip} complete: {len(paintings)} / {total_paintings}"
          " paintings..."
      )

      if len(paintings) >= total_paintings:
        break

      skip += PAGE_LIMIT
      time.sleep(0.1)  # Brief pause to avoid rate limiting

    except requests.exceptions.RequestException as e:
      print(f"Error while downloading at offset {skip}: {e}")
      break

  # Save the raw file
  with open(output_path, "w", encoding="utf-8") as f:
    json.dump(paintings, f, ensure_ascii=False, indent=2)

  print(
      f"Cleveland extraction completed successfully! Saved"
      f" {len(paintings)} paintings to:\n{output_path}"
  )


if __name__ == "__main__":
  extract_all_cleveland_paintings()