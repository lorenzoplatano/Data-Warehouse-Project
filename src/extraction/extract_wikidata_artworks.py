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
BATCH_SIZE = 50


def collect_artworks_to_query(processed_dir: Path, raw_dir: Path) -> list:
  artworks = []

  # 1. Chicago
  chicago_file = processed_dir / "chicago_cleaned.json"
  if chicago_file.exists():
    with open(chicago_file, "r", encoding="utf-8") as f:
      for r in json.load(f):
        artworks.append({
            "museum": "The Art Institute of Chicago",
            "source_id": str(r["source_id"]),
            "qid": None,
        })

  # 2. Met
  met_file = processed_dir / "met_cleaned.json"
  if met_file.exists():
    with open(met_file, "r", encoding="utf-8") as f:
      for r in json.load(f):
        artworks.append({
            "museum": "The Metropolitan Museum of Art",
            "source_id": str(r["source_id"]),
            "qid": None,
        })

  # 3. Cleveland (retrieve the QID if present in the raw data)
  cleveland_raw = raw_dir / "cleveland_raw.json"
  qid_map = {}
  if cleveland_raw.exists():
    with open(cleveland_raw, "r", encoding="utf-8") as f:
      for item in json.load(f):
        sid = str(item.get("id"))
        wiki_url = item.get("external_resources", {}).get("wikidata", [])
        if wiki_url and isinstance(wiki_url, list):
          qid = wiki_url[0].split("/")[-1]
          if qid.startswith("Q"):
            qid_map[sid] = qid

  cleveland_file = processed_dir / "cleveland_cleaned.json"
  if cleveland_file.exists():
    with open(cleveland_file, "r", encoding="utf-8") as f:
      for r in json.load(f):
        sid = str(r["source_id"])
        artworks.append({
            "museum": "The Cleveland Museum of Art",
            "source_id": sid,
            "qid": qid_map.get(sid),
        })

  return artworks


def query_movements_batch(batch: list) -> dict:
  results = {}

  chicago_ids = " ".join(
      [
          f'"{item["source_id"]}"'
          for item in batch
          if item["museum"] == "The Art Institute of Chicago"
      ]
  )
  met_ids = " ".join(
      [
          f'"{item["source_id"]}"'
          for item in batch
          if item["museum"] == "The Metropolitan Museum of Art"
      ]
  )
  cleveland_qids = " ".join(
      [f'wd:{item["qid"]}' for item in batch if item.get("qid")]
  )

  clauses = []
  if chicago_ids:
    clauses.append(f"""
      {{
        VALUES ?chicagoId {{ {chicago_ids} }}
        ?item wdt:P4610 ?chicagoId;
              wdt:P135 ?mov.
        BIND("The Art Institute of Chicago" AS ?museum)
        BIND(?chicagoId AS ?source_id)
      }}
    """)
  if met_ids:
    clauses.append(f"""
      {{
        VALUES ?metId {{ {met_ids} }}
        ?item wdt:P3634 ?metId;
              wdt:P135 ?mov.
        BIND("The Metropolitan Museum of Art" AS ?museum)
        BIND(?metId AS ?source_id)
      }}
    """)
  if cleveland_qids:
    clauses.append(f"""
      {{
        VALUES ?item {{ {cleveland_qids} }}
        ?item wdt:P135 ?mov.
        BIND("The Cleveland Museum of Art" AS ?museum)
        BIND(STRAFTER(STR(?item), "/entity/") AS ?source_id)
      }}
    """)

  if not clauses:
    return {}

  query = f"""
    SELECT ?museum ?source_id ?movLabel ?epochLabel WHERE {{
      {(" UNION ".join(clauses))}
      OPTIONAL {{ ?mov wdt:P2348 ?epoch. }}
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
        for b in resp.json().get("results", {}).get("bindings", []):
          mus = b.get("museum", {}).get("value")
          sid = b.get("source_id", {}).get("value")
          mov = b.get("movLabel", {}).get("value")
          epoch = b.get("epochLabel", {}).get("value", "Modern Era")
          key = f"{mus}|{sid}"
          if key not in results:
            results[key] = {
                "museum": mus,
                "source_id": sid,
                "movement": mov,
                "historical_epoch": epoch,
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
  output_file = raw_dir / "wikidata_artworks.json"

  artworks_data = {}
  if output_file.exists():
    with open(output_file, "r", encoding="utf-8") as f:
      try:
        artworks_data = json.load(f)
      except json.JSONDecodeError:
        artworks_data = {}

  all_artworks = collect_artworks_to_query(processed_dir, raw_dir)
  pending = [
      a for a in all_artworks if f"{a['museum']}|{a['source_id']}" not in artworks_data
  ]

  print("=== WIKIDATA EXTRACTION: ARTWORK MOVEMENTS ===")
  print(f"Total artworks in files: {len(all_artworks)}")
  print(f"Already cached: {len(artworks_data)}")
  print(f"To process: {len(pending)}")

  start_time = time.time()
  for i in range(0, len(pending), BATCH_SIZE):
    batch = pending[i : i + BATCH_SIZE]
    res = query_movements_batch(batch)
    artworks_data.update(res)

    done = min(i + BATCH_SIZE, len(pending))
    print(
        f"Progress: {done}/{len(pending)} | Artworks with a movement found:"
        f" {len(artworks_data)}"
    )

    if (i // BATCH_SIZE) % 8 == 0:
      with open(output_file, "w", encoding="utf-8") as f:
        json.dump(artworks_data, f, ensure_ascii=False, indent=2)
    time.sleep(0.4)

  with open(output_file, "w", encoding="utf-8") as f:
    json.dump(artworks_data, f, ensure_ascii=False, indent=2)

  print(
      f"Completed in {(time.time() - start_time) / 60:.2f} min! Saved to"
      f" {output_file}"
  )


if __name__ == "__main__":
  run()