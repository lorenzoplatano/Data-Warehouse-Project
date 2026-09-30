-- name: insert_museums
INSERT INTO dim_museum (museum_name)
VALUES (%s)
ON CONFLICT (museum_name) DO NOTHING;

-- name: select_museums
SELECT museum_name, id_museum FROM dim_museum;

-- name: insert_geography
INSERT INTO dim_geography (country_name, macro_region, continent)
VALUES (%s, %s, %s)
ON CONFLICT (country_name) DO UPDATE
SET macro_region = CASE
        WHEN dim_geography.macro_region = 'Unknown'
             AND EXCLUDED.macro_region <> 'Unknown'
        THEN EXCLUDED.macro_region
        ELSE dim_geography.macro_region
    END,
    continent = CASE
        WHEN dim_geography.continent = 'Unknown'
             AND EXCLUDED.continent <> 'Unknown'
        THEN EXCLUDED.continent
        ELSE dim_geography.continent
    END;

-- name: select_geography
SELECT country_name, id_country FROM dim_geography;

-- name: insert_movements
INSERT INTO dim_movement (movement_name, historical_epoch)
VALUES (%s, %s)
ON CONFLICT (movement_name) DO NOTHING;

-- name: select_movements
SELECT movement_name, id_movement FROM dim_movement;

-- name: insert_time
INSERT INTO dim_time (id_year, decade, century, historical_epoch)
VALUES (%s, %s, %s, %s)
ON CONFLICT (id_year) DO NOTHING;

-- name: insert_techniques
INSERT INTO dim_technique (id_technique, technique_full, technique_type, material_type)
VALUES (%s, %s, %s, %s)
ON CONFLICT (id_technique) DO NOTHING;

-- name: insert_artists
INSERT INTO dim_artist (artist_name, birth_date, death_date, id_nationality_country)
VALUES (%s, %s, %s, %s);

-- name: select_artists
SELECT artist_name, id_artist FROM dim_artist;

-- name: insert_artworks
INSERT INTO fact_artworks (
    title, source_id, id_museum, id_start_year, id_end_year,
    id_movement, id_technique, id_artist, id_origin_country,
    height_cm, width_cm, area_cm2, production_duration
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
