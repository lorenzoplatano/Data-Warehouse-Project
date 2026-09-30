-- Drop existing tables to allow clean reruns
DROP TABLE IF EXISTS fact_artworks CASCADE;
DROP TABLE IF EXISTS dim_artist CASCADE;
DROP TABLE IF EXISTS dim_geography CASCADE;
DROP TABLE IF EXISTS dim_technique CASCADE;
DROP TABLE IF EXISTS dim_movement CASCADE;
DROP TABLE IF EXISTS dim_time CASCADE;
DROP TABLE IF EXISTS dim_museum CASCADE;

-- 1. Museum dimension
CREATE TABLE dim_museum (
    id_museum SERIAL PRIMARY KEY,
    museum_name VARCHAR(100) NOT NULL UNIQUE
);

-- 2. Geography dimension (shared hierarchy)
CREATE TABLE dim_geography (
    id_country SERIAL PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL UNIQUE,
    macro_region VARCHAR(100) NOT NULL,
    continent VARCHAR(50) NOT NULL
);

-- 3. Movement dimension
CREATE TABLE dim_movement (
    id_movement SERIAL PRIMARY KEY,
    movement_name VARCHAR(150) NOT NULL UNIQUE,
    historical_epoch VARCHAR(100) NOT NULL
);

-- 4. Time dimension
CREATE TABLE dim_time (
    id_year INT PRIMARY KEY,
    decade INT NOT NULL,
    century VARCHAR(30) NOT NULL,
    historical_epoch VARCHAR(100) NOT NULL
);

-- 5. Technique dimension (orthogonal DAG)
CREATE TABLE dim_technique (
    id_technique SERIAL PRIMARY KEY,
    technique_full VARCHAR(255) NOT NULL UNIQUE,
    technique_type VARCHAR(100) NOT NULL,
    material_type VARCHAR(100) NOT NULL
);

-- 6. Artist dimension
CREATE TABLE dim_artist (
    id_artist SERIAL PRIMARY KEY,
    artist_name VARCHAR(255) NOT NULL,
    birth_date INT,
    death_date INT,
    id_nationality_country INT REFERENCES dim_geography(id_country)
);

-- 7. Fact table: artwork
CREATE TABLE fact_artworks (
    id_artwork SERIAL PRIMARY KEY,
    title VARCHAR(500),
    source_id VARCHAR(100) NOT NULL,

    -- Foreign Keys
    id_museum INT NOT NULL REFERENCES dim_museum(id_museum),
    id_start_year INT REFERENCES dim_time(id_year),
    id_end_year INT REFERENCES dim_time(id_year),
    id_movement INT REFERENCES dim_movement(id_movement),
    id_technique INT REFERENCES dim_technique(id_technique),
    id_artist INT REFERENCES dim_artist(id_artist),
    id_origin_country INT REFERENCES dim_geography(id_country),

    -- Measurements
    height_cm NUMERIC(10, 2),
    width_cm NUMERIC(10, 2),
    area_cm2 NUMERIC(12, 2),
    production_duration INT
);

-- Sentinel records (ID = 0 to handle NULL or missing values)
INSERT INTO dim_museum (id_museum, museum_name)
VALUES (0, 'Unknown / Not Specified') ON CONFLICT DO NOTHING;

INSERT INTO dim_geography (id_country, country_name, macro_region, continent)
VALUES (0, 'Unknown', 'Unknown', 'Unknown') ON CONFLICT DO NOTHING;

INSERT INTO dim_movement (id_movement, movement_name, historical_epoch)
VALUES (0, 'Unknown', 'Unknown') ON CONFLICT DO NOTHING;

INSERT INTO dim_time (id_year, decade, century, historical_epoch)
VALUES (0, 0, 'Unknown', 'Unknown') ON CONFLICT DO NOTHING;

INSERT INTO dim_technique (id_technique, technique_full, technique_type, material_type)
VALUES (0, 'Unknown', 'Unknown', 'Unknown') ON CONFLICT DO NOTHING;

INSERT INTO dim_artist (id_artist, artist_name, birth_date, death_date, id_nationality_country)
VALUES (0, 'Unknown Artist', NULL, NULL, 0) ON CONFLICT DO NOTHING;