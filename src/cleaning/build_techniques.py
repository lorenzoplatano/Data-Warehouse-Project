import json
import re
from pathlib import Path


def parse_technique_and_support(raw_str):
  if not raw_str or not isinstance(raw_str, str):
    return "Unknown Technique", "Unknown Support"

  text = raw_str.lower().strip()

  # 1. Identify the technique (binder/medium)
  technique = "Unknown Technique"
  if "oil" in text or "olio" in text:
    technique = "Oil"
  elif "tempera" in text:
    technique = "Tempera"
  elif "watercolor" in text or "watercolour" in text or "acquerello" in text:
    technique = "Watercolor"
  elif "acrylic" in text or "acrilico" in text:
    technique = "Acrylic"
  elif "gouache" in text or "guazzo" in text:
    technique = "Gouache"
  elif "encaustic" in text or "encausto" in text:
    technique = "Encaustic"
  elif "distemper" in text:
    technique = "Distemper"
  elif "fresco" in text or "affresco" in text:
    technique = "Fresco"
  elif "ink" in text or "inchiostro" in text:
    technique = "Ink"
  elif "mixed media" in text:
    technique = "Mixed Media"

  # 2. Identify the support (base material)
  support = "Unknown Support"
  if "canvas" in text or "tela" in text or "linen" in text or "fabric" in text:
    support = "Canvas"
  elif "panel" in text or "wood" in text or "tavola" in text or "legno" in text:
    support = "Wood Panel"
  elif (
      "paper" in text
      or "carta" in text
      or "cardboard" in text
      or "board" in text
      or "cartone" in text
  ):
    support = "Paper/Cardboard"
  elif "copper" in text or "rame" in text:
    support = "Copper"
  elif "ivory" in text or "avorio" in text:
    support = "Ivory"
  elif "silk" in text or "seta" in text:
    support = "Silk"
  elif "masonite" in text or "hardboard" in text:
    support = "Masonite"
  elif "glass" in text or "vetro" in text:
    support = "Glass"
  elif "metal" in text or "steel" in text or "alluminio" in text:
    support = "Metal"

  return technique, support


def build_techniques_dimension():
  project_root = Path(__file__).resolve().parents[2]
  processed_dir = project_root / "data" / "processed"
  interim_dir = project_root / "data" / "interim"
  interim_dir.mkdir(parents=True, exist_ok=True)

  chicago_file = processed_dir / "chicago_cleaned.json"
  cleveland_file = processed_dir / "cleveland_cleaned.json"
  met_file = processed_dir / "met_cleaned.json"

  print("=== Building the Orthogonal Techniques and Supports Dimension ===")

  all_mediums = set()
  for path in [chicago_file, cleveland_file, met_file]:
    if path.exists():
      with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)
        for r in records:
          m = r.get("medium_raw")
          if m:
            all_mediums.add(m)

  print(f"Unique medium strings found: {len(all_mediums)}")

  # Sentinel record required for DFM compliance
  techniques_dim = [{
      "technique_id": 0,
      "technique_type": "Unknown Technique",
      "material_type": "Unknown Support",
      "raw_description": "Unknown/Unspecified",
  }]

  medium_to_id = {}
  current_id = 1

  # Group unique combinations (technique_type, material_type)
  combo_to_id = {}

  for medium in sorted(all_mediums):
    tech, supp = parse_technique_and_support(medium)
    combo = (tech, supp)

    if combo not in combo_to_id:
      combo_to_id[combo] = current_id
      techniques_dim.append({
          "technique_id": current_id,
          "technique_type": tech,
          "material_type": supp,
          "raw_description": medium,
      })
      current_id += 1

    medium_to_id[medium] = combo_to_id[combo]

  # 1. Save the dimension table
  dim_output_path = processed_dir / "dim_technique.json"
  with open(dim_output_path, "w", encoding="utf-8") as f:
    json.dump(techniques_dim, f, ensure_ascii=False, indent=2)

  # 2. Save the lookup map (for the fact-loading stage)
  map_output_path = interim_dir / "medium_to_technique_id.json"
  with open(map_output_path, "w", encoding="utf-8") as f:
    json.dump(medium_to_id, f, ensure_ascii=False, indent=2)

  print(
      f"Generated {len(techniques_dim)} dimension records (including ID 0) in:\n"
      f"{dim_output_path}"
  )
  print(
      f"Saved lookup map ({len(medium_to_id)} mappings) to:\n"
      f"{map_output_path}"
  )


if __name__ == "__main__":
  build_techniques_dimension()