from pathlib import Path
import json
import pandas as pd
import requests

# Official URL for the Met Open Access dataset on GitHub
MET_CSV_URL = "https://media.githubusercontent.com/media/metmuseum/openaccess/master/MetObjects.csv"


def extract_met_paintings():
    project_root = Path(__file__).resolve().parents[2]
    output_dir = project_root / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "met_raw.json"

    print("=== 1. Downloading the official Met Open Access data dump ===")
    print("Downloading (this takes about 15-30 seconds)...")

    # Read the compressed file directly with pandas
    df = pd.read_csv(
        MET_CSV_URL,
        low_memory=False,
        dtype=str  # Preserve codes and text fields as-is
    )
    print(f"Met dataset loaded! Total records in collection: {len(df)}")

    print("\n=== 2. Filtering for paintings only ===")
    # Filter by classification or object name
    is_painting = (
            df["Classification"].str.contains("Painting", case=False, na=False) |
            df["Object Name"].str.contains("Painting", case=False, na=False)
    )
    # Exclude duplicates and rows without a title
    paintings_df = df[is_painting & df["Title"].notna()].copy()
    print(f"Total paintings found: {len(paintings_df)}")

    print("\n=== 3. Mapping fields to JSON format ===")
    records = []
    for _, row in paintings_df.iterrows():
        records.append({
            "objectID": int(row["Object ID"]) if pd.notna(row["Object ID"]) else None,
            "title": row["Title"],
            "artistDisplayName": row["Artist Display Name"] if pd.notna(row["Artist Display Name"]) else None,
            "artistDisplayBio": row["Artist Display Bio"] if pd.notna(row["Artist Display Bio"]) else None,
            "artistBeginDate": row["Artist Begin Date"] if pd.notna(row["Artist Begin Date"]) else None,
            "artistEndDate": row["Artist End Date"] if pd.notna(row["Artist End Date"]) else None,
            "artistNationality": row["Artist Nationality"] if pd.notna(row["Artist Nationality"]) else None,
            "objectBeginDate": int(row["Object Begin Date"]) if pd.notna(row["Object Begin Date"]) and row[
                "Object Begin Date"].lstrip("-").isdigit() else None,
            "objectEndDate": int(row["Object End Date"]) if pd.notna(row["Object End Date"]) and row[
                "Object End Date"].lstrip("-").isdigit() else None,
            "medium": row["Medium"] if pd.notna(row["Medium"]) else None,
            "dimensions": row["Dimensions"] if pd.notna(row["Dimensions"]) else None,
            "country": row["Country"] if pd.notna(row["Country"]) else None,
            "culture": row["Culture"] if pd.notna(row["Culture"]) else None,
            "classification": row["Classification"] if pd.notna(row["Classification"]) else None,
            "department": row["Department"] if pd.notna(row["Department"]) else None
        })

    print(f"\n=== 4. Saving to disk at: {output_path} ===")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"Met extraction completed successfully! Saved {len(records)} paintings.")


if __name__ == "__main__":
    extract_met_paintings()