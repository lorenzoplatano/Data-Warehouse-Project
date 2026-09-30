import json
from pathlib import Path

# Deterministic movement-to-seven-canonical-historical-periods mapping
MOVEMENT_TO_EPOCH = {
    # 1. Ancient Era (Origins – AD 476)
    "Roman art": "Ancient Era",
    "Fayum mummy portraits": "Ancient Era",

    # 2. Middle Ages (476 – ~1400)
    "International Gothic": "Middle Ages",
    "Gothic art": "Middle Ages",
    "Proto-Renaissance": "Middle Ages",
    "Sienese school": "Middle Ages",
    "Florentine School": "Middle Ages",
    "Northern Landscape style": "Middle Ages",

    # 3. Renaissance & Mannerism (~1400 – 1600)
    "Renaissance": "Renaissance & Mannerism",
    "Early Renaissance": "Renaissance & Mannerism",
    "High Renaissance": "Renaissance & Mannerism",
    "German Renaissance": "Renaissance & Mannerism",
    "Spanish Renaissance": "Renaissance & Mannerism",
    "Northern Renaissance": "Renaissance & Mannerism",
    "Italian Renaissance": "Renaissance & Mannerism",
    "Italian Renaissance painting": "Renaissance & Mannerism",
    "French Renaissance": "Renaissance & Mannerism",
    "Mannerism": "Renaissance & Mannerism",
    "Northern Mannerism": "Renaissance & Mannerism",
    "Early Netherlandish painting": "Renaissance & Mannerism",
    "Venetian school": "Renaissance & Mannerism",
    "Veronese school": "Renaissance & Mannerism",
    "Cretan school": "Renaissance & Mannerism",
    "School of Fontainebleau": "Renaissance & Mannerism",
    "Quattrocento": "Renaissance & Mannerism",
    "Zhe school": "Renaissance & Mannerism",
    "Nine Friends of Painting": "Renaissance & Mannerism",

    # 4. Baroque & Rococo (~1600 – 1780)
    "Baroque": "Baroque & Rococo",
    "Baroque painting": "Baroque & Rococo",
    "Italian Baroque painting": "Baroque & Rococo",
    "Spanish Baroque painting": "Baroque & Rococo",
    "Flemish Baroque painting": "Baroque & Rococo",
    "Dutch Golden Age painting": "Baroque & Rococo",
    "Caravaggisti": "Baroque & Rococo",
    "Utrecht Caravaggism": "Baroque & Rococo",
    "tenebrism": "Baroque & Rococo",
    "Rococo": "Baroque & Rococo",
    "Classicism": "Baroque & Rococo",
    "Bolognese school": "Baroque & Rococo",
    "fijnschilder": "Baroque & Rococo",
    "Mughal painting": "Baroque & Rococo",
    "Pahari painting": "Baroque & Rococo",
    "Hishikawa school": "Baroque & Rococo",
    "Xin'an School": "Baroque & Rococo",
    "Western painting": "Baroque & Rococo",
    "Shijō school": "Baroque & Rococo",

    # 5. 19th Century Movements (1780 – ~1880)
    "Neoclassicism": "19th Century Movements",
    "Pre-romanticism": "19th Century Movements",
    "Romanticism": "19th Century Movements",
    "German Romanticism": "19th Century Movements",
    "Troubadour style": "19th Century Movements",
    "academic art": "19th Century Movements",
    "realism": "19th Century Movements",
    "French Realism": "19th Century Movements",
    "American realism": "19th Century Movements",
    "Barbizon school": "19th Century Movements",
    "American Barbizon school": "19th Century Movements",
    "Hudson River school": "19th Century Movements",
    "Danish Golden Age": "19th Century Movements",
    "Düsseldorf school of painting": "19th Century Movements",
    "École d'Écouen": "19th Century Movements",
    "Orientalism": "19th Century Movements",
    "Orientalist painting": "19th Century Movements",
    "Pre-Raphaelite Brotherhood": "19th Century Movements",
    "Naturalism": "19th Century Movements",
    "luminism": "19th Century Movements",
    "Tonalism": "19th Century Movements",
    "Macchiaioli": "19th Century Movements",
    "Hague School": "19th Century Movements",
    "Official Salon of Painting and Sculpture": "19th Century Movements",
    "anti-clerical art": "19th Century Movements",

    # 6. Modernism & Avant-Garde (~1880 – 1945)
    "Impressionism": "Modernism & Avant-Garde",
    "American Impressionism": "Modernism & Avant-Garde",
    "Post-impressionism": "Modernism & Avant-Garde",
    "Neo-impressionism": "Modernism & Avant-Garde",
    "pointillism": "Modernism & Avant-Garde",
    "Symbolism": "Modernism & Avant-Garde",
    "Aestheticism": "Modernism & Avant-Garde",
    "Arts and Crafts movement": "Modernism & Avant-Garde",
    "Art Nouveau": "Modernism & Avant-Garde",
    "Catalan modernism": "Modernism & Avant-Garde",
    "Japonisme": "Modernism & Avant-Garde",
    "Fauvism": "Modernism & Avant-Garde",
    "Expressionism": "Modernism & Avant-Garde",
    "cubism": "Modernism & Avant-Garde",
    "analytical cubism": "Modernism & Avant-Garde",
    "Cezannian cubism": "Modernism & Avant-Garde",
    "Section d'Or": "Modernism & Avant-Garde",
    "Futurism": "Modernism & Avant-Garde",
    "Russian Futurism": "Modernism & Avant-Garde",
    "Russian avant-garde": "Modernism & Avant-Garde",
    "Constructivism": "Modernism & Avant-Garde",
    "Suprematism": "Modernism & Avant-Garde",
    "De Stijl": "Modernism & Avant-Garde",
    "Dada": "Modernism & Avant-Garde",
    "surrealism": "Modernism & Avant-Garde",
    "Belgian surrealism": "Modernism & Avant-Garde",
    "metaphysical painting": "Modernism & Avant-Garde",
    "Bauhaus": "Modernism & Avant-Garde",
    "Precisionism": "Modernism & Avant-Garde",
    "Ashcan School": "Modernism & Avant-Garde",
    "Regionalism": "Modernism & Avant-Garde",
    "American scene painting": "Modernism & Avant-Garde",
    "social realism": "Modernism & Avant-Garde",
    "magic realism": "Modernism & Avant-Garde",
    "Harlem Renaissance": "Modernism & Avant-Garde",
    "School of Paris": "Modernism & Avant-Garde",
    "Pont-Aven School": "Modernism & Avant-Garde",
    "Les Nabis": "Modernism & Avant-Garde",
    "Lingnan School": "Modernism & Avant-Garde",
    "Nihonga": "Modernism & Avant-Garde",
    "naïve art": "Modernism & Avant-Garde",
    "Picasso's Blue Period": "Modernism & Avant-Garde",
    "Picasso's Rose Period": "Modernism & Avant-Garde",
    "modern art": "Modernism & Avant-Garde",
    "modernism": "Modernism & Avant-Garde",
    "American modernism": "Modernism & Avant-Garde",
    "pictorialism": "Modernism & Avant-Garde",

    # 7. Post-War & Contemporary (1945 – Present)
    "abstract art": "Post-War & Contemporary",
    "abstract expressionism": "Post-War & Contemporary",
    "Color Field": "Post-War & Contemporary",
    "Washington Color School": "Post-War & Contemporary",
    "hard-edge painting": "Post-War & Contemporary",
    "geometric abstraction": "Post-War & Contemporary",
    "lyrical abstraction": "Post-War & Contemporary",
    "art brut": "Post-War & Contemporary",
    "Informalism": "Post-War & Contemporary",
    "COBRA": "Post-War & Contemporary",
    "Fluxus": "Post-War & Contemporary",
    "pop art": "Post-War & Contemporary",
    "op art": "Post-War & Contemporary",
    "Minimalism": "Post-War & Contemporary",
    "postminimalism": "Post-War & Contemporary",
    "conceptual art": "Post-War & Contemporary",
    "contemporary art": "Post-War & Contemporary",
    "environmental art": "Post-War & Contemporary",
    "feminist art": "Post-War & Contemporary",
    "photorealism": "Post-War & Contemporary",
    "neo-expressionism": "Post-War & Contemporary",
    "Chicago Imagists": "Post-War & Contemporary",
    "Postmodernism": "Post-War & Contemporary",
    "Hurufiyya movement": "Post-War & Contemporary",
    "Antropophagia": "Post-War & Contemporary",
    "capitalist realism": "Post-War & Contemporary",
    "Black Atlantic": "Post-War & Contemporary",
    "Young British Artists": "Post-War & Contemporary",
    "Allusive Abstractionists": "Post-War & Contemporary",
}

# Fallback when the raw movement is not mapped but the raw period indicates a century
EPOCH_FALLBACK_RULES = {
    "16th century": "Renaissance & Mannerism",
    "15th century": "Renaissance & Mannerism",
    "14th century": "Middle Ages",
    "13th century": "Middle Ages",
    "17th century": "Baroque & Rococo",
    "18th century": "Baroque & Rococo",
    "Baroque": "Baroque & Rococo",
    "Habsburg Netherlands": "Baroque & Rococo",
    "19th century": "19th Century Movements",
    "Victorian era": "19th Century Movements",
    "Modern Era": "Modernism & Avant-Garde",
    "Middle Ages": "Middle Ages",
}


def clean_movement_name(raw_name: str) -> str:
    """Format the movement name in title case and remove anomalous characters."""
    if not raw_name or raw_name.startswith("Q"):
        return None
    # Apply consistent title case formatting
    clean = " ".join([word.capitalize() for word in raw_name.strip().split()])
    return clean


def resolve_canonical_epoch(clean_mov: str, raw_epoch: str) -> str:
    """Resolve the historical period into the seven canonical categories."""
    # 1. Look up the movement directly in the movement dictionary
    for mov_key, epoch_val in MOVEMENT_TO_EPOCH.items():
        if mov_key.lower() == clean_mov.lower():
            return epoch_val

    # 2. Resolve using the previously extracted fallback value
    if raw_epoch in EPOCH_FALLBACK_RULES:
        return EPOCH_FALLBACK_RULES[raw_epoch]

    return "Modernism & Avant-Garde"  # Conservative default


def run():
    project_root = Path(__file__).resolve().parents[2]
    processed_dir = project_root / "data" / "processed"

    raw_dir = project_root / "data" / "raw"

    # Look for the file with or without the _2 suffix
    input_file = raw_dir / "wikidata_artworks_2.json"
    if not input_file.exists():
        input_file = raw_dir / "wikidata_artworks.json"

    output_file = processed_dir / "wikidata_artworks_cleaned.json"

    if not input_file.exists():
        print(f"Error: file not found at {input_file}")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        artworks_data = json.load(f)

    cleaned_artworks = {}
    cleaned_count = 0
    discarded_qid_count = 0

    for key, data in artworks_data.items():
        raw_mov = data.get("movement")
        raw_epoch = data.get("historical_epoch")

        # Filter out unresolved QIDs (e.g. Q125731576)
        if raw_mov and raw_mov.startswith("Q") and raw_mov[1:].isdigit():
            discarded_qid_count += 1
            continue

        clean_mov = clean_movement_name(raw_mov)
        if clean_mov:
            canonical_epoch = resolve_canonical_epoch(clean_mov, raw_epoch)
            cleaned_artworks[key] = {
                "museum": data.get("museum"),
                "source_id": str(data.get("source_id")),
                "movement": clean_mov,
                "historical_epoch": canonical_epoch
            }
            cleaned_count += 1

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cleaned_artworks, f, ensure_ascii=False, indent=2)

    print("=== WIKIDATA ARTWORKS CLEANING COMPLETED ===")
    print(f"Source file: {input_file.name}")
    print(f"Valid artworks saved: {cleaned_count}")
    print(f"Artworks discarded due to unresolved QIDs: {discarded_qid_count}")
    print(f"File saved to: {output_file}\n")


if __name__ == "__main__":
    run()