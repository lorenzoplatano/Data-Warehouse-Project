# src/utils/geo_utils.py
import re

GLOBAL_GEO_MAP = {
    # --- Northern America ---
    "america": ("United States", "Northern America", "Americas"),
    "american": ("United States", "Northern America", "Americas"),
    "united states": ("United States", "Northern America", "Americas"),
    "united states of america": ("United States", "Northern America", "Americas"),
    "usa": ("United States", "Northern America", "Americas"),
    "u.s.a.": ("United States", "Northern America", "Americas"),
    "new york": ("United States", "Northern America", "Americas"),
    "new york city": ("United States", "Northern America", "Americas"),
    "boston": ("United States", "Northern America", "Americas"),
    "pueblo of pojoaque": ("United States", "Northern America", "Americas"),
    "new mexico": ("United States", "Northern America", "Americas"),
    "massachusetts": ("United States", "Northern America", "Americas"),
    "abiquiu": ("United States", "Northern America", "Americas"),
    "lake george": ("United States", "Northern America", "Americas"),
    "taos": ("United States", "Northern America", "Americas"),
    "greenwich": ("United States", "Northern America", "Americas"),
    "fulton": ("United States", "Northern America", "Americas"),
    "wyoming": ("United States", "Northern America", "Americas"),
    "philadelphia": ("United States", "Northern America", "Americas"),
    "prouts neck": ("United States", "Northern America", "Americas"),
    "ipswich": ("United States", "Northern America", "Americas"),
    "chappaqua": ("United States", "Northern America", "Americas"),
    "chicago": ("United States", "Northern America", "Americas"),
    "florida": ("United States", "Northern America", "Americas"),
    "new hampshire": ("United States", "Northern America", "Americas"),
    "long island": ("United States", "Northern America", "Americas"),
    "los angeles": ("United States", "Northern America", "Americas"),
    "gloucester": ("United States", "Northern America", "Americas"),
    "connecticut": ("United States", "Northern America", "Americas"),
    "michigan": ("United States", "Northern America", "Americas"),
    "montana": ("United States", "Northern America", "Americas"),
    "pennsylvania": ("United States", "Northern America", "Americas"),
    "saint louis": ("United States", "Northern America", "Americas"),
    "york harbor": ("United States", "Northern America", "Americas"),
    "baltimore": ("United States", "Northern America", "Americas"),
    "bath": ("United States", "Northern America", "Americas"),
    "bennington": ("United States", "Northern America", "Americas"),
    "captiva": ("United States", "Northern America", "Americas"),
    "cedar rapids": ("United States", "Northern America", "Americas"),
    "easton": ("United States", "Northern America", "Americas"),
    "hartford": ("United States", "Northern America", "Americas"),
    "illinois": ("United States", "Northern America", "Americas"),
    "martha's vineyard": ("United States", "Northern America", "Americas"),
    "mills pond": ("United States", "Northern America", "Americas"),
    "nantucket island": ("United States", "Northern America", "Americas"),
    "niagara falls": ("United States", "Northern America", "Americas"),
    "virginia": ("United States", "Northern America", "Americas"),
    "new jersey": ("United States", "Northern America", "Americas"),
    "newport": ("United States", "Northern America", "Americas"),
    "roxbury": ("United States", "Northern America", "Americas"),
    "loch vale": ("United States", "Northern America", "Americas"),
    "long beach": ("United States", "Northern America", "Americas"),
    "confederated salish and kootenai tribes of the flathead reservation": ("United States", "Northern America",
                                                                            "Americas"),

    "canada": ("Canada", "Northern America", "Americas"),
    "mexico": ("Mexico", "Central America", "Americas"),
    "mexican": ("Mexico", "Central America", "Americas"),
    "teotihuacán": ("Mexico", "Central America", "Americas"),

    # --- Western and Southern Europe ---
    "france": ("France", "Western Europe", "Europe"),
    "french": ("France", "Western Europe", "Europe"),
    "paris": ("France", "Western Europe", "Europe"),
    "giverny": ("France", "Western Europe", "Europe"),
    "château du bréau": ("France", "Western Europe", "Europe"),
    "saint-rémy-de-provence": ("France", "Western Europe", "Europe"),
    "brittany": ("France", "Western Europe", "Europe"),
    "trouville": ("France", "Western Europe", "Europe"),

    "italy": ("Italy", "Southern Europe", "Europe"),
    "italian": ("Italy", "Southern Europe", "Europe"),
    "venice": ("Italy", "Southern Europe", "Europe"),
    "rome": ("Italy", "Southern Europe", "Europe"),
    "florence": ("Italy", "Southern Europe", "Europe"),
    "genoa": ("Italy", "Southern Europe", "Europe"),
    "frascati": ("Italy", "Southern Europe", "Europe"),
    "naples": ("Italy", "Southern Europe", "Europe"),
    "siena": ("Italy", "Southern Europe", "Europe"),
    "pisa": ("Italy", "Southern Europe", "Europe"),
    "tuscany": ("Italy", "Southern Europe", "Europe"),
    "northern italy": ("Italy", "Southern Europe", "Europe"),
    "roman": ("Italy", "Southern Europe", "Europe"),
    "roman, pompeian": ("Italy", "Southern Europe", "Europe"),
    "feltre": ("Italy", "Southern Europe", "Europe"),
    "bologna": ("Italy", "Southern Europe", "Europe"),
    "umbria": ("Italy", "Southern Europe", "Europe"),
    "antonine-era roman empire (egypt)": ("Italy", "Southern Europe", "Europe"),
    "unknown (italian style)": ("Italy", "Southern Europe", "Europe"),

    "united kingdom": ("United Kingdom", "Northern Europe", "Europe"),
    "england": ("United Kingdom", "Northern Europe", "Europe"),
    "great britain": ("United Kingdom", "Northern Europe", "Europe"),
    "britain": ("United Kingdom", "Northern Europe", "Europe"),
    "british": ("United Kingdom", "Northern Europe", "Europe"),
    "uk": ("United Kingdom", "Northern Europe", "Europe"),
    "london": ("United Kingdom", "Northern Europe", "Europe"),
    "scotland": ("United Kingdom", "Northern Europe", "Europe"),
    "scottish": ("United Kingdom", "Northern Europe", "Europe"),
    "lancaster": ("United Kingdom", "Northern Europe", "Europe"),
    "northern ireland": ("United Kingdom", "Northern Europe", "Europe"),
    "jersey": ("United Kingdom", "Northern Europe", "Europe"),

    "netherlands": ("Netherlands", "Western Europe", "Europe"),
    "holland": ("Netherlands", "Western Europe", "Europe"),
    "delft": ("Netherlands", "Western Europe", "Europe"),
    "dutch": ("Netherlands", "Western Europe", "Europe"),
    "dordrecht": ("Netherlands", "Western Europe", "Europe"),
    "netherlandish": ("Netherlands", "Western Europe", "Europe"),
    "amsterdam": ("Netherlands", "Western Europe", "Europe"),

    "belgium": ("Belgium", "Western Europe", "Europe"),
    "flanders": ("Belgium", "Western Europe", "Europe"),
    "bruges": ("Belgium", "Western Europe", "Europe"),
    "leuven": ("Belgium", "Western Europe", "Europe"),
    "flemish": ("Belgium", "Western Europe", "Europe"),
    "south netherlandish": ("Belgium", "Western Europe", "Europe"),

    "germany": ("Germany", "Western Europe", "Europe"),
    "german": ("Germany", "Western Europe", "Europe"),
    "cologne": ("Germany", "Western Europe", "Europe"),
    "strasbourg": ("Germany", "Western Europe", "Europe"),
    "munich": ("Germany", "Western Europe", "Europe"),
    "bavaria, probably munich": ("Germany", "Western Europe", "Europe"),
    "rhine": ("Germany", "Western Europe", "Europe"),

    "austria": ("Austria", "Western Europe", "Europe"),

    "spain": ("Spain", "Southern Europe", "Europe"),
    "spanish": ("Spain", "Southern Europe", "Europe"),
    "catalonia": ("Spain", "Southern Europe", "Europe"),
    "seville": ("Spain", "Southern Europe", "Europe"),
    "madrid": ("Spain", "Southern Europe", "Europe"),

    "greece": ("Greece", "Southern Europe", "Europe"),
    "kríti": ("Greece", "Southern Europe", "Europe"),
    "crete ?": ("Greece", "Southern Europe", "Europe"),
    "corfu": ("Greece", "Southern Europe", "Europe"),
    "byzantine": ("Greece", "Southern Europe", "Europe"),
    "byzantium, constantinople": ("Greece", "Southern Europe", "Europe"),

    "russia": ("Russia", "Eastern Europe", "Europe"),
    "denmark": ("Denmark", "Northern Europe", "Europe"),
    "sweden": ("Sweden", "Northern Europe", "Europe"),
    "norway": ("Norway", "Northern Europe", "Europe"),
    "romania": ("Romania", "Eastern Europe", "Europe"),
    "czechoslovakia": ("Czech Republic", "Eastern Europe", "Europe"),
    "bohemian": ("Czech Republic", "Eastern Europe", "Europe"),
    "ireland": ("Ireland", "Northern Europe", "Europe"),
    "uzbekistan": ("Uzbekistan", "Central Asia", "Asia"),

    # --- Asia ---
    "china": ("China", "Eastern Asia", "Asia"),
    "chinese, ming dynasty": ("China", "Eastern Asia", "Asia"),
    "guangdong": ("China", "Eastern Asia", "Asia"),
    "sino-tibetan": ("China", "Eastern Asia", "Asia"),

    "japan": ("Japan", "Eastern Asia", "Asia"),
    "kyoto": ("Japan", "Eastern Asia", "Asia"),
    "ueno": ("Japan", "Eastern Asia", "Asia"),

    "south korea": ("South Korea", "Eastern Asia", "Asia"),
    "korea": ("South Korea", "Eastern Asia", "Asia"),
    "taiwan": ("Taiwan", "Eastern Asia", "Asia"),
    "mongolia": ("Mongolia", "Eastern Asia", "Asia"),

    "india": ("India", "Southern Asia", "Asia"),
    "thanjavur": ("India", "Southern Asia", "Asia"),
    "nepal": ("Nepal", "Southern Asia", "Asia"),
    "nepal, kathmandu": ("Nepal", "Southern Asia", "Asia"),
    "nepal, kathmandu valley": ("Nepal", "Southern Asia", "Asia"),
    "rajasthan": ("India", "Southern Asia", "Asia"),
    "bihar": ("India", "Southern Asia", "Asia"),
    "west bengal": ("India", "Southern Asia", "Asia"),
    "puri": ("India", "Southern Asia", "Asia"),
    "nathdwara": ("India", "Southern Asia", "Asia"),
    "kushan": ("India", "Southern Asia", "Asia"),
    "murshidabad": ("India", "Southern Asia", "Asia"),
    "jaipur": ("India", "Southern Asia", "Asia"),
    "maharashtra": ("India", "Southern Asia", "Asia"),
    "andhra pradesh": ("India", "Southern Asia", "Asia"),
    "avadh": ("India", "Southern Asia", "Asia"),
    "bundi": ("India", "Southern Asia", "Asia"),
    "gujarat": ("India", "Southern Asia", "Asia"),
    "hyderabad": ("India", "Southern Asia", "Asia"),
    "jahangirabad": ("India", "Southern Asia", "Asia"),
    "jodhpur": ("India", "Southern Asia", "Asia"),
    "kota": ("India", "Southern Asia", "Asia"),
    "lucknow": ("India", "Southern Asia", "Asia"),
    "mysore": ("India", "Southern Asia", "Asia"),
    "sri lanka": ("Sri Lanka", "Southern Asia", "Asia"),
    "bangladesh": ("Bangladesh", "Southern Asia", "Asia"),
    "thailand": ("Thailand", "South-Eastern Asia", "Asia"),
    "bali": ("Indonesia", "South-Eastern Asia", "Asia"),
    "deccan": ("India", "Southern Asia", "Asia"),

    "tibet": ("China", "Eastern Asia", "Asia"),
    "central tibet": ("China", "Eastern Asia", "Asia"),
    "central tibet, ngor monastery": ("China", "Eastern Asia", "Asia"),
    "western tibet": ("China", "Eastern Asia", "Asia"),
    "western tibet, tholing monastery": ("China", "Eastern Asia", "Asia"),
    "central asia, kizil": ("China", "Eastern Asia", "Asia"),

    "iraq": ("Iraq", "Western Asia", "Asia"),
    "shiraz": ("Iran", "Western Asia", "Asia"),
    "turkey": ("Turkey", "Western Asia", "Asia"),
    "persia": ("Iran", "Western Asia", "Asia"),
    "herat": ("Afghanistan", "Southern Asia", "Asia"),
    "isfahan": ("Iran", "Western Asia", "Asia"),
    "israel": ("Israel", "Western Asia", "Asia"),
    "pakistan": ("Pakistan", "Southern Asia", "Asia"),
    "middle east": ("Middle East", "Western Asia", "Asia"),

    # --- Africa ---
    "egypt": ("Egypt", "Northern Africa", "Africa"),
    "al fayyum": ("Egypt", "Northern Africa", "Africa"),
    "ethiopia": ("Ethiopia", "Eastern Africa", "Africa"),
    "mozambique": ("Mozambique", "Eastern Africa", "Africa"),
    "africa, mozambique": ("Mozambique", "Eastern Africa", "Africa"),
    "côte d'ivoire": ("Ivory Coast", "Western Africa", "Africa"),
    "ivory coast": ("Ivory Coast", "Western Africa", "Africa"),
    "algeria": ("Algeria", "Northern Africa", "Africa"),
    "cape town": ("South Africa", "Southern Africa", "Africa"),

    # --- Latin America and Oceania ---
    "uruguay": ("Uruguay", "South America", "Americas"),
    "peru (cuzco)": ("Peru", "South America", "Americas"),
    "peruvian (cuzco)": ("Peru", "South America", "Americas"),
    "peruvian north coast": ("Peru", "South America", "Americas"),
    "chile": ("Chile", "South America", "Americas"),
    "bolivia": ("Bolivia", "South America", "Americas"),
    "ecuador (quito)": ("Ecuador", "South America", "Americas"),
    "colombia": ("Colombia", "South America", "Americas"),
    "cuba": ("Cuba", "Caribbean", "Americas"),

    "papua new guinea": ("Papua New Guinea", "Melanesia", "Oceania"),
    "australia, western arnhem land": ("Australia", "Australasia", "Oceania"),

    # --- General or Broad Categories ---
    "the west": ("Unknown", "Unknown", "Unknown"),
    "european": ("Europe", "Europe", "Europe"),
    "europe": ("Europe", "Europe", "Europe"),

# Remaining Cuzco entries and style variants:
    "peru cuzco": ("Peru", "South America", "Americas"),
    "peruvian cuzco": ("Peru", "South America", "Americas"),
    "ecuador quito": ("Ecuador", "South America", "Americas"),
    "unknown": ("Italy", "Southern Europe", "Europe"),
    "peru": ("Peru", "South America", "Americas"),
    "ecuador": ("Ecuador", "South America", "Americas"),
}


def normalize_geography(place_raw):
    """
    Given a raw string, return a dictionary with the standardized geographic hierarchy.
    """
    if not place_raw or not isinstance(place_raw, str):
        return {
            "country": "Unknown",
            "macro_region": "Unknown",
            "continent": "Unknown"
        }

    p = place_raw.lower().strip()
    p = re.sub(r'\(.*?\)', '', p)
    p = re.sub(r',\s*(13th|14th|15th|16th|17th|18th|19th|20th|21st)\s*century.*', '', p)
    p = re.sub(r',\s*(late|early|mid|period|unknown).*', '', p)
    p = p.strip()

    if p in GLOBAL_GEO_MAP:
        c, m, cont = GLOBAL_GEO_MAP[p]
        return {"country": c, "macro_region": m, "continent": cont}

    parts = [sub.strip() for sub in p.split(',')]
    for part in parts:
        if part in GLOBAL_GEO_MAP:
            c, m, cont = GLOBAL_GEO_MAP[part]
            return {"country": c, "macro_region": m, "continent": cont}

    for key, (c, m, cont) in GLOBAL_GEO_MAP.items():
        if key in p:
            return {"country": c, "macro_region": m, "continent": cont}

    return {
        "country": place_raw.strip(),
        "macro_region": "Unknown",
        "continent": "Unknown"
    }