import os
import json
import requests

# Met Museum API endpoints
SEARCH_URL = "https://collectionapi.metmuseum.org/public/collection/v1/search"
OBJECT_URL = "https://collectionapi.metmuseum.org/public/collection/v1/objects/"

# Target file path relative to this script
output_dir = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "raw", "samples"
    )
)
output_path = os.path.join(output_dir, "sample_met.json")

# Ensure the raw directory exists
os.makedirs(output_dir, exist_ok=True)

try:
    # Search for paintings instead of taking the first objects returned by the API.
    response = requests.get(
        SEARCH_URL,
        params={
            "q": "painting",
            "medium": "Paintings",
            "hasImages": "true",
        },
    )
    response.raise_for_status()
    object_ids = response.json().get("objectIDs", [])[:10]  # First 10 items for testing

    artworks = []
    for obj_id in object_ids:
        res = requests.get(f"{OBJECT_URL}{obj_id}")
        res.raise_for_status()
        data = res.json()
        if data.get("title"):
            artworks.append(data)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(artworks, f, ensure_ascii=False, indent=4)

    print(f"Data successfully saved to {output_path}")
except Exception as e:
    print(f"Extraction error: {e}")