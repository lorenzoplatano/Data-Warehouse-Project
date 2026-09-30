import json
from pathlib import Path
import time
import requests

WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"
HEADERS = {
    "User-Agent": (
        "MuseumDWHProject/2.0 (Academic Research; Data Warehouse Project;"
        " contact: student@university.it)"
    )
}
BATCH_SIZE = 25


def get_unique_artists(processed_dir: Path) -> list:
  artists = set()
  for filename in [
      "chicago_cleaned.json",
      "cleveland_cleaned.json",
      "met_cleaned.json",
  ]:
    filepath = processed_dir / filename
    if filepath.exists():
      with open(filepath, "r", encoding="utf-8") as f:
        for r in json.load(f):
          name = r.get("artist_name")
          if name and name != "Unknown Artist":
            clean_name = name.replace('"', '\\"').strip()
            if len(clean_name) > 1:
              artists.add(clean_name)
  return sorted(list(artists))


def query_artists_batch(artist_batch: list) -> dict:
  values_clause = " ".join([f'"{name}"@en' for name in artist_batch])
  query = f"""
    SELECT ?name ?birthDate ?deathDate ?countryLabel ?movementLabel ?epochLabel WHERE {{
      VALUES ?name {{ {values_clause} }}
      ?artist ?label ?name;
              wdt:P106/wdt:P279* wd:Q1028181. # Painter

      OPTIONAL {{ ?artist wdt:P569 ?birthDate. }}
      OPTIONAL {{ ?artist wdt:P570 ?deathDate. }}

      OPTIONAL {{
        {{ ?artist wdt:P27 ?country. }}
        UNION
        {{ ?artist wdt:P19/wdt:P17 ?country. }}
      }}

      OPTIONAL {{
        ?artist wdt:P135 ?movement.
        OPTIONAL {{ ?movement wdt:P2348 ?epoch. }}
      }}

      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """
  for attempt in range(3):
    try:
      resp = requests.get(
          WIKIDATA_SPARQL_URL,
          params={"query": query, "format": "json"},
          headers=HEADERS,
          timeout=30,
      )
      if resp.status_code == 200:
        results = {}
        for b in resp.json().get("results", {}).get("bindings", []):
          raw_name = b.get("name", {}).get("value")
          if not raw_name or raw_name in results:
            continue
          birth = b.get("birthDate", {}).get("value")
          death = b.get("deathDate", {}).get("value")
          results[raw_name] = {
              "artist_name": raw_name,
              "birth_year": (
                  int(birth[:4])
                  if birth and (birth[:4].isdigit() or birth.startswith("-"))
                  else None
              ),
              "death_year": (
                  int(death[:4])
                  if death and (death[:4].isdigit() or death.startswith("-"))
                  else None
              ),
              "nationality": b.get("countryLabel", {}).get("value"),
              "artist_movement": b.get("movementLabel", {}).get("value"),
              "historical_epoch": b.get("epochLabel", {}).get("value"),
          }
        return results
      elif resp.status_code in [429, 500, 502, 503, 504]:
        time.sleep((attempt + 1) * 3)
    except requests.exceptions.RequestException:
      time.sleep((attempt + 1) * 3)
  return {}


def run():
  project_root = Path(__file__).resolve().parents[2]
  processed_dir = project_root / "data" / "processed"
  raw_dir = project_root / "data" / "raw"
  output_file = raw_dir / "wikidata_artists.json"

  artists_data = {}
  if output_file.exists():
    with open(output_file, "r", encoding="utf-8") as f:
      try:
        artists_data = json.load(f)
      except json.JSONDecodeError:
        artists_data = {}

  all_artists = get_unique_artists(processed_dir)
  pending = [a for a in all_artists if a not in artists_data]

  print("=== WIKIDATA EXTRACTION: ARTISTS (Biography + Movement Fallback) ===")
  print(f"Unique artists: {len(all_artists)}")
  print(f"Already cached: {len(artists_data)}")
  print(f"To process: {len(pending)}")

  start_time = time.time()
  for i in range(0, len(pending), BATCH_SIZE):
    batch = pending[i : i + BATCH_SIZE]
    res = query_artists_batch(batch)
    artists_data.update(res)

    done = min(i + BATCH_SIZE, len(pending))
    print(
        f"Progress: {done}/{len(pending)} | Total with data:"
        f" {len(artists_data)}"
    )

    if (i // BATCH_SIZE) % 8 == 0:
      with open(output_file, "w", encoding="utf-8") as f:
        json.dump(artists_data, f, ensure_ascii=False, indent=2)
    time.sleep(0.4)

  with open(output_file, "w", encoding="utf-8") as f:
    json.dump(artists_data, f, ensure_ascii=False, indent=2)

  print(
      f"Completed in {(time.time() - start_time) / 60:.2f} min! Saved to"
      f" {output_file}"
  )


if __name__ == "__main__":
  run()