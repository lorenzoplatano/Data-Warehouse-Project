import os
import json
import requests

# Art Institute of Chicago public API endpoint
URL = "https://api.artic.edu/api/v1/artworks?limit=100"

# Target file path relative to this script
output_dir = os.path.join("..", "..", "data", "raw", "samples")
output_path = os.path.join(output_dir, "sample_chicago.json")

# Ensure the raw directory exists
os.makedirs(output_dir, exist_ok=True)

try:
    response = requests.get(URL)
    response.raise_for_status()
    data = response.json()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Data successfully saved to {output_path}")
except Exception as e:
    print(f"Extraction error: {e}")