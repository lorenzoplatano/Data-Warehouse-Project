import json
import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_batch
from db_config import DB_CONFIG

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PROCESSED = BASE_DIR / "data" / "processed"
DATA_INTERIM = BASE_DIR / "data" / "interim"

MUSEUM_FILES = [
    DATA_PROCESSED / "chicago_cleaned.json",
    DATA_PROCESSED / "cleveland_cleaned.json",
    DATA_PROCESSED / "met_cleaned.json",
]
DIM_TECHNIQUE_FILE = DATA_PROCESSED / "dim_technique.json"
MEDIUM_MAP_FILE = DATA_INTERIM / "medium_to_technique_id.json"
WIKIDATA_ARTISTS_FILE = DATA_PROCESSED / "wikidata_artists_cleaned.json"
WIKIDATA_ARTWORKS_FILE = DATA_PROCESSED / "wikidata_artworks_cleaned.json"
SQL_FILE = BASE_DIR / "sql" / "load_dw.sql"

def load_sql_queries():
    queries = {}
    current_name = None
    current_lines = []

    with SQL_FILE.open("r", encoding="utf-8") as sql_file:
        for line in sql_file:
            if line.startswith("-- name:"):
                if current_name is not None:
                    queries[current_name] = "\n".join(current_lines).strip().removesuffix(";")

                current_name = line.partition(":")[2].strip()
                if not current_name or current_name in queries:
                    raise ValueError(f"Invalid or duplicate SQL query name: {current_name!r}")
                current_lines = []
            elif current_name is not None:
                current_lines.append(line)

    if current_name is not None:
        queries[current_name] = "\n".join(current_lines).strip().removesuffix(";")
    if not queries or any(not query for query in queries.values()):
        raise ValueError(f"No valid named SQL queries found in {SQL_FILE}")

    return queries


def load_json(filepath):
    if not os.path.exists(filepath):
        print(f"[X] File not found: {filepath}")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_to_list(raw_data, default_key_name=None):
    if isinstance(raw_data, list):
        return [x for x in raw_data if isinstance(x, dict)]
    if isinstance(raw_data, dict):
        result = []
        for key, val in raw_data.items():
            if isinstance(val, dict):
                item = val.copy()
                if default_key_name and default_key_name not in item:
                    item[default_key_name] = key
                result.append(item)
            elif isinstance(val, str) and default_key_name:
                result.append({default_key_name: val})
        return result
    return []


def calculate_time_attributes(year: int):
    if year == 0:
        return 0, "Unknown", "Unknown"

    decade = (year // 10) * 10

    if year > 0:
        century_num = (year - 1) // 100 + 1
        century = f"{century_num}th Century"
        if year < 500:
            epoch = "Ancient / Classical Antiquity"
        elif year < 1400:
            epoch = "Middle Ages"
        elif year < 1600:
            epoch = "Renaissance"
        elif year < 1750:
            epoch = "Baroque"
        elif year < 1850:
            epoch = "18th-19th Century"
        elif year < 1945:
            epoch = "Modern"
        else:
            epoch = "Contemporary"
    else:
        abs_yr = abs(year)
        century_num = (abs_yr - 1) // 100 + 1
        century = f"{century_num}th Century BC"
        epoch = "Ancient (BC)"

    return decade, century, epoch


def main():
    print("[*] Connecting to PostgreSQL (museum_dw)...")
    queries = load_sql_queries()
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
    except Exception as e:
        print(f"[X] Connection error: {e}")
        sys.exit(1)

    try:
        # 1. dim_museum
        print("[*] Populating dim_museum...")
        museum_names = set()
        for fpath in MUSEUM_FILES:
            for item in load_json(fpath):
                m_name = item.get("museum_name")
                if m_name:
                    museum_names.add(m_name.strip())

        cur.executemany(queries["insert_museums"], [(m,) for m in museum_names])
        conn.commit()

        cur.execute(queries["select_museums"])
        museum_lookup = {row[0].lower(): row[1] for row in cur.fetchall()}
        museum_lookup["unknown"] = 0

        # 2. dim_geography
        print("[*] Populating dim_geography...")
        artists_data = normalize_to_list(load_json(WIKIDATA_ARTISTS_FILE), "artist_name")
        artworks_wd = normalize_to_list(load_json(WIKIDATA_ARTWORKS_FILE))

        geo_set = {}
        for item in artists_data + artworks_wd:
            c = item.get("country") or item.get("country_name") or (item.get("geo_hierarchy") or {}).get("country")
            if c and c.strip():
                c_clean = c.strip()
                macro = item.get("macro_region") or (item.get("geo_hierarchy") or {}).get("macro_region") or "Unknown"
                cont = item.get("continent") or (item.get("geo_hierarchy") or {}).get("continent") or "Unknown"
                if c_clean.lower() not in geo_set:
                    geo_set[c_clean.lower()] = (c_clean, macro, cont)

        # Also add normalized countries from the cleaned museum files.
        for fpath in MUSEUM_FILES:
            for item in load_json(fpath):
                c = item.get("place_raw")
                if isinstance(c, str) and c.strip():
                    c_clean = c.strip()
                    macro = item.get("macro_region") or "Unknown"
                    cont = item.get("continent") or "Unknown"
                    key = c_clean.lower()
                    existing = geo_set.get(key)
                    if existing is None:
                        geo_set[key] = (c_clean, macro, cont)
                    else:
                        country, existing_macro, existing_cont = existing
                        geo_set[key] = (
                            country,
                            macro if existing_macro == "Unknown" and macro != "Unknown" else existing_macro,
                            cont if existing_cont == "Unknown" and cont != "Unknown" else existing_cont,
                        )

        cur.executemany(queries["insert_geography"], list(geo_set.values()))
        conn.commit()

        cur.execute(queries["select_geography"])
        geo_lookup = {row[0].lower(): row[1] for row in cur.fetchall()}
        geo_lookup["unknown"] = 0

        # 3. dim_movement
        print("[*] Populating dim_movement...")
        mov_map = {}
        for item in artworks_wd + artists_data:
            m = item.get("movement") or item.get("movement_name") or item.get("artist_movement")
            epoch = item.get("historical_epoch") or item.get("canonical_epoch") or "Unknown"
            if m and m.strip():
                m_clean = m.strip()
                if m_clean.lower() not in mov_map:
                    mov_map[m_clean.lower()] = (m_clean, epoch)

        cur.executemany(queries["insert_movements"], list(mov_map.values()))
        conn.commit()

        cur.execute(queries["select_movements"])
        movement_lookup = {row[0].lower(): row[1] for row in cur.fetchall()}
        movement_lookup["unknown"] = 0

        # 4. dim_time
        print("[*] Populating dim_time...")
        years_found = set()
        for fpath in MUSEUM_FILES:
            for art in load_json(fpath):
                s_yr = art.get("start_year")
                e_yr = art.get("end_year")
                if s_yr is not None and isinstance(s_yr, int):
                    years_found.add(s_yr)
                if e_yr is not None and isinstance(e_yr, int):
                    years_found.add(e_yr)

        time_records = []
        for yr in years_found:
            dec, cent, ep = calculate_time_attributes(yr)
            time_records.append((yr, dec, cent, ep))

        cur.executemany(queries["insert_time"], time_records)
        conn.commit()

        # 5. dim_technique
        print("[*] Populating dim_technique...")
        dim_tech_data = load_json(DIM_TECHNIQUE_FILE)
        technique_rows = []
        for t in dim_tech_data:
            t_id = t.get("technique_id")
            if t_id == 0 or t_id is None:
                continue
            full_desc = t.get("raw_description") or f"{t.get('technique_type', '')} on {t.get('material_type', '')}"
            technique_rows.append((
                t_id,
                full_desc.strip(),
                t.get("technique_type", "Unknown"),
                t.get("material_type", "Unknown")
            ))

        cur.executemany(queries["insert_techniques"], technique_rows)
        conn.commit()

        med_map_data = load_json(MEDIUM_MAP_FILE)
        medium_map = {item["medium_raw"]: item["technique_id"] for item in med_map_data if isinstance(item, dict)} if isinstance(med_map_data, list) else med_map_data

        # 6. dim_artist
        print("[*] Populating dim_artist...")
        artists_to_insert = []
        seen_artists = set()

        for a in artists_data:
            name = a.get("artist_name")
            if not name or name.strip().lower() in seen_artists:
                continue
            seen_artists.add(name.strip().lower())

            b_date = a.get("birth_year") or a.get("birth_date")
            d_date = a.get("death_year") or a.get("death_date")

            try:
                b_date = int(b_date) if b_date is not None else None
            except (ValueError, TypeError):
                b_date = None

            try:
                d_date = int(d_date) if d_date is not None else None
            except (ValueError, TypeError):
                d_date = None

            country_name = (a.get("country_normalized") or a.get("country") or "").lower().strip()
            id_country = geo_lookup.get(country_name, 0)

            artists_to_insert.append((name.strip(), b_date, d_date, id_country))

        cur.executemany(queries["insert_artists"], artists_to_insert)
        conn.commit()

        cur.execute(queries["select_artists"])
        artist_lookup = {row[0].lower(): row[1] for row in cur.fetchall()}
        artist_lookup["unknown artist"] = 0

        # Artist-to-movement mapping based on wikidata_artists_cleaned.
        artist_to_movement = {}
        for a in artists_data:
            a_n = a.get("artist_name")
            mov = a.get("artist_movement") or a.get("movement")
            if a_n and mov:
                artist_to_movement[a_n.strip().lower()] = movement_lookup.get(mov.lower().strip(), 0)

        # Wikidata artwork (museum|source_id)-to-movement mapping.
        artwork_mov_lookup = {}
        for item in artworks_wd:
            m_key = item.get("museum")
            s_id = item.get("source_id")
            mov = item.get("movement")
            if m_key and s_id and mov:
                artwork_mov_lookup[(m_key.lower().strip(), str(s_id).strip())] = movement_lookup.get(mov.lower().strip(), 0)

        # 7. fact_artworks
        print("[*] Populating fact_artworks...")
        facts_to_insert = []

        for fpath in MUSEUM_FILES:
            museum_artworks = load_json(fpath)
            for art in museum_artworks:
                title = art.get("title") or "Untitled"
                source_id = str(art.get("source_id")).strip()

                museum_raw = art.get("museum_name") or ""
                id_museum = museum_lookup.get(museum_raw.lower().strip(), 0)

                s_yr = art.get("start_year")
                id_start_year = s_yr if (s_yr is not None and s_yr in years_found) else 0

                e_yr = art.get("end_year")
                id_end_year = e_yr if (e_yr is not None and e_yr in years_found) else 0

                a_name = art.get("artist_name")
                id_artist = artist_lookup.get(a_name.lower().strip(), 0) if a_name else 0

                # Resolve the movement from wikidata_artworks first, then from the artist; otherwise use 0.
                id_movement = artwork_mov_lookup.get((museum_raw.lower().strip(), source_id), 0)
                if id_movement == 0 and a_name:
                    id_movement = artist_to_movement.get(a_name.lower().strip(), 0)

                m_raw = art.get("medium_raw")
                id_technique = medium_map.get(m_raw, 0)

                # Use place_raw directly; it is already normalized in the _cleaned.json files.
                p_raw = art.get("place_raw")
                id_origin_country = geo_lookup.get(p_raw.lower().strip(), 0) if p_raw and isinstance(p_raw, str) else 0

                facts_to_insert.append((
                    title,
                    source_id,
                    id_museum,
                    id_start_year,
                    id_end_year,
                    id_movement,
                    id_technique,
                    id_artist,
                    id_origin_country,
                    art.get("height_cm"),
                    art.get("width_cm"),
                    art.get("area_cm2"),
                    art.get("production_duration")
                ))

        execute_batch(cur, queries["insert_artworks"], facts_to_insert, page_size=1000)

        conn.commit()
        print(f"[+] fact_artworks populated successfully ({len(facts_to_insert)} records).")
        print("\n[V] DATA WAREHOUSE FULLY LOADED AND SUCCESSFULLY LINKED!")

    except Exception as e:
        conn.rollback()
        print(f"[X] Critical loading error: {e}")
        raise e
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()