import os
import json
import requests

# Official Cleveland Museum of Art Open Access API (No API key needed)
URL = "https://openaccess-api.clevelandart.org/api/artworks/?limit=20&has_image=1"

output_dir = os.path.join("..", "..", "data", "raw", "samples")
output_path = os.path.join(output_dir, "sample_cleveland.json")

os.makedirs(output_dir, exist_ok=True)

try:
    response = requests.get(URL)
    response.raise_for_status()
    data = response.json()

    # Get the raw list of 20 detailed artworks
    artworks = data.get("data", [])

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(artworks, f, ensure_ascii=False, indent=4)

    print(f"Data successfully saved to {output_path} ({len(artworks)} artworks)")
except Exception as e:
    print(f"Extraction error: {e}")