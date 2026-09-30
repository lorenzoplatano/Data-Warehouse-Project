import json
from pathlib import Path


# 1. NATIONALITY MAPPING

NATIONALITY_CANONICAL_MAP = {
    # Italy and pre-unification states
    "Italy": ("Italy", "Southern Europe", "Europe"),
    "Italian": ("Italy", "Southern Europe", "Europe"),
    "Republic of Venice": ("Italy", "Southern Europe", "Europe"),
    "Republic of Florence": ("Italy", "Southern Europe", "Europe"),
    "Duchy of Modena and Reggio": ("Italy", "Southern Europe", "Europe"),

    # China and historical dynasties
    "People's Republic of China": ("China", "Eastern Asia", "Asia"),
    "Republic of China": ("China", "Eastern Asia", "Asia"),
    "Ming dynasty": ("China", "Eastern Asia", "Asia"),
    "Qing dynasty": ("China", "Eastern Asia", "Asia"),
    "Yuan dynasty": ("China", "Eastern Asia", "Asia"),
    "Song dynasty": ("China", "Eastern Asia", "Asia"),
    "Southern Song dynasty": ("China", "Eastern Asia", "Asia"),

    # Benelux region
    "Netherlands": ("Netherlands", "Western Europe", "Europe"),
    "Dutch": ("Netherlands", "Western Europe", "Europe"),
    "Kingdom of the Netherlands": ("Netherlands", "Western Europe", "Europe"),
    "Belgium": ("Belgium", "Western Europe", "Europe"),
    "Habsburg Netherlands": ("Belgium", "Western Europe", "Europe"),
    "Luxembourg": ("Luxembourg", "Western Europe", "Europe"),

    # British Isles
    "United Kingdom": ("United Kingdom", "Northern Europe", "Europe"),
    "United Kingdom of Great Britain and Ireland": ("United Kingdom", "Northern Europe", "Europe"),
    "British": ("United Kingdom", "Northern Europe", "Europe"),
    "Ireland": ("Ireland", "Northern Europe", "Europe"),

    # German-speaking area and Central Europe
    "Germany": ("Germany", "Western Europe", "Europe"),
    "Austria": ("Austria", "Western Europe", "Europe"),
    "Austrian Empire": ("Austria", "Western Europe", "Europe"),
    "Switzerland": ("Switzerland", "Western Europe", "Europe"),
    "Czech Republic": ("Czech Republic", "Eastern Europe", "Europe"),
    "Hungary": ("Hungary", "Eastern Europe", "Europe"),
    "Second Hungarian Republic": ("Hungary", "Eastern Europe", "Europe"),
    "Poland": ("Poland", "Eastern Europe", "Europe"),
    "Slovenia": ("Slovenia", "Southern Europe", "Europe"),
    "Croatia": ("Croatia", "Southern Europe", "Europe"),

    # Russia and Eastern Europe
    "Russia": ("Russia", "Eastern Europe", "Europe"),
    "Russian Empire": ("Russia", "Eastern Europe", "Europe"),
    "Ukraine": ("Ukraine", "Eastern Europe", "Europe"),
    "Belarus": ("Belarus", "Eastern Europe", "Europe"),
    "Lithuania": ("Lithuania", "Northern Europe", "Europe"),
    "Latvia": ("Latvia", "Northern Europe", "Europe"),
    "Romania": ("Romania", "Eastern Europe", "Europe"),
    "Moldova": ("Moldova", "Eastern Europe", "Europe"),

    # Iberian Peninsula
    "Spain": ("Spain", "Southern Europe", "Europe"),
    "Kingdom of Aragon": ("Spain", "Southern Europe", "Europe"),
    "Portugal": ("Portugal", "Southern Europe", "Europe"),
    "Kingdom of Portugal": ("Portugal", "Southern Europe", "Europe"),

    # France
    "France": ("France", "Western Europe", "Europe"),

    # Scandinavia
    "Sweden": ("Sweden", "Northern Europe", "Europe"),
    "Denmark": ("Denmark", "Northern Europe", "Europe"),
    "Norway": ("Norway", "Northern Europe", "Europe"),
    "Finland": ("Finland", "Northern Europe", "Europe"),

    # North America
    "United States": ("United States", "Northern America", "Americas"),
    "United States Virgin Islands": ("United States", "Northern America", "Americas"),
    "Canada": ("Canada", "Northern America", "Americas"),
    "Mexico": ("Mexico", "Central America", "Americas"),

    # Latin America and the Caribbean
    "Brazil": ("Brazil", "South America", "Americas"),
    "Argentina": ("Argentina", "South America", "Americas"),
    "Uruguay": ("Uruguay", "South America", "Americas"),
    "Colombia": ("Colombia", "South America", "Americas"),
    "Venezuela": ("Venezuela", "South America", "Americas"),
    "Cuba": ("Cuba", "Caribbean", "Americas"),
    "Dominican Republic": ("Dominican Republic", "Caribbean", "Americas"),
    "Haiti": ("Haiti", "Caribbean", "Americas"),
    "Guatemala": ("Guatemala", "Central America", "Americas"),
    "Viceroyalty of Peru": ("Peru", "South America", "Americas"),
    "Peru": ("Peru", "South America", "Americas"),
    "Guyana": ("Guyana", "South America", "Americas"),

    # Asia and Oceania
    "Japan": ("Japan", "Eastern Asia", "Asia"),
    "Tokugawa shogunate": ("Japan", "Eastern Asia", "Asia"),
    "South Korea": ("South Korea", "Eastern Asia", "Asia"),
    "Korea": ("South Korea", "Eastern Asia", "Asia"),
    "Taiwan": ("Taiwan", "Eastern Asia", "Asia"),
    "Joseon": ("South Korea", "Eastern Asia", "Asia"),
    "Later Silla": ("South Korea", "Eastern Asia", "Asia"),
    "India": ("India", "Southern Asia", "Asia"),
    "Mughal Empire": ("India", "Southern Asia", "Asia"),
    "Kingdom of Mewar": ("India", "Southern Asia", "Asia"),
    "Guler State": ("India", "Southern Asia", "Asia"),
    "Oudh State": ("India", "Southern Asia", "Asia"),
    "Pakistan": ("Pakistan", "Southern Asia", "Asia"),
    "Iran": ("Iran", "Western Asia", "Asia"),
    "Iraq": ("Iraq", "Western Asia", "Asia"),
    "Turkey": ("Turkey", "Western Asia", "Asia"),
    "Lebanon": ("Lebanon", "Western Asia", "Asia"),
    "Palestine": ("Palestine", "Western Asia", "Asia"),
    "Indonesia": ("Indonesia", "South-Eastern Asia", "Asia"),
    "Philippines": ("Philippines", "South-Eastern Asia", "Asia"),
    "Afghanistan": ("Afghanistan", "Southern Asia", "Asia"),
    "Australia": ("Australia", "Australasia", "Oceania"),

    # Africa
    "Egypt": ("Egypt", "Northern Africa", "Africa"),
    "Sudan": ("Sudan", "Northern Africa", "Africa"),
    "Ghana": ("Ghana", "Western Africa", "Africa"),
    "Nigeria": ("Nigeria", "Western Africa", "Africa"),
    "South Africa": ("South Africa", "Southern Africa", "Africa"),
    "Ethiopia": ("Ethiopia", "Eastern Africa", "Africa"),
    "Democratic Republic of the Congo": ("Democratic Republic of the Congo", "Middle Africa", "Africa"),

    # Greece
    "Greece": ("Greece", "Southern Europe", "Europe"),
}

# 2. MOVEMENT MAPPING

MOVEMENT_TO_EPOCH = {
    # 1. Ancient Era
    "Roman art": "Ancient Era",
    "Fayum mummy portraits": "Ancient Era",

    # 2. Middle Ages
    "International Gothic": "Middle Ages",
    "Gothic art": "Middle Ages",
    "Proto-Renaissance": "Middle Ages",
    "Sienese school": "Middle Ages",
    "Florentine School": "Middle Ages",
    "Northern Landscape style": "Middle Ages",

    # 3. Renaissance & Mannerism
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

    # 4. Baroque & Rococo
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

    # 5. 19th Century Movements
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

    # 6. Modernism & Avant-Garde
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

    # 7. Post-War & Contemporary
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


def clean_movement_name(raw_name: str) -> str:
    if not raw_name or (raw_name.startswith("Q") and raw_name[1:].isdigit()):
        return None
    return " ".join([w.capitalize() for w in raw_name.strip().split()])


def derive_epoch_by_year(birth_year: int) -> str:
    if not birth_year:
        return "Unknown Epoch"
    if birth_year < 476:
        return "Ancient Era"
    elif birth_year < 1400:
        return "Middle Ages"
    elif birth_year < 1600:
        return "Renaissance & Mannerism"
    elif birth_year < 1780:
        return "Baroque & Rococo"
    elif birth_year < 1880:
        return "19th Century Movements"
    elif birth_year < 1945:
        return "Modernism & Avant-Garde"
    else:
        return "Post-War & Contemporary"


def resolve_artist_epoch(clean_mov: str, birth_year: int) -> str:
    if clean_mov:
        for mov_key, epoch_val in MOVEMENT_TO_EPOCH.items():
            if mov_key.lower() == clean_mov.lower():
                return epoch_val
    return derive_epoch_by_year(birth_year)


def run():
    project_root = Path(__file__).resolve().parents[2]
    raw_dir = project_root / "data" / "raw"
    processed_dir = project_root / "data" / "processed"

    processed_dir.mkdir(parents=True, exist_ok=True)

    input_file = raw_dir / "wikidata_artists_2.json"
    if not input_file.exists():
        input_file = raw_dir / "wikidata_artists.json"

    output_file = processed_dir / "wikidata_artists_cleaned.json"

    if not input_file.exists():
        print(f"Error: artist source file not found in {raw_dir}")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        artists_data = json.load(f)

    cleaned_artists = {}
    normalized_nat_count = 0
    resolved_mov_count = 0

    for artist_name, data in artists_data.items():
        raw_nat = data.get("nationality")
        norm_country = None
        geo_hierarchy = None

        if raw_nat and not (raw_nat.startswith("Q") and raw_nat[1:].isdigit()):
            geo_info = NATIONALITY_CANONICAL_MAP.get(raw_nat)
            if geo_info:
                norm_country, macro_reg, cont = geo_info
                geo_hierarchy = {
                    "country": norm_country,
                    "macro_region": macro_reg,
                    "continent": cont
                }
                normalized_nat_count += 1

        raw_mov = data.get("artist_movement")
        clean_mov = clean_movement_name(raw_mov)
        if clean_mov:
            resolved_mov_count += 1

        birth_yr = data.get("birth_year")
        canonical_epoch = resolve_artist_epoch(clean_mov, birth_yr)

        cleaned_artists[artist_name] = {
            "artist_name": artist_name,
            "birth_year": birth_yr,
            "death_year": data.get("death_year"),
            "nationality_raw": raw_nat,
            "country_normalized": norm_country,
            "geo_hierarchy": geo_hierarchy,
            "artist_movement": clean_mov,
            "historical_epoch": canonical_epoch
        }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cleaned_artists, f, ensure_ascii=False, indent=2)

    print("=== WIKIDATA ARTISTS CLEANING COMPLETED ===")
    print(f"Input read from: {input_file}")
    print(f"Total artists processed: {len(cleaned_artists)}")
    print(f"Nationalities normalized to modern countries: {normalized_nat_count}")
    print(f"Artists with standardized movements: {resolved_mov_count}")
    print(f"Output saved to: {output_file}\n")


if __name__ == "__main__":
    run()