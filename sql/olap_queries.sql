-- OLAP QUERIES

-- 1. Does each museum's collection have a prevalence of artists from a specific macroregion?
WITH MacroMuseumStats AS (
    SELECT
        g.macro_region,
        mu.museum_name,
        COUNT(f.id_artwork) AS total_artworks,
        COUNT(DISTINCT f.id_artist) AS unique_artists
    FROM fact_artworks f
    JOIN dim_museum mu ON f.id_museum = mu.id_museum
    JOIN dim_artist a ON f.id_artist = a.id_artist
    JOIN dim_geography g ON a.id_nationality_country = g.id_country
    WHERE mu.id_museum != 0
      AND f.id_artist != 0
      AND g.macro_region IS NOT NULL
      AND g.macro_region != 'Unknown'
      AND a.artist_name NOT IN ('India')
    GROUP BY g.macro_region, mu.museum_name
),
PivotedMacro AS (
    SELECT
        macro_region,
        MAX(CASE WHEN museum_name = 'Art Institute of Chicago' THEN total_artworks || ' works (' || unique_artists || ' artists)' END) AS chicago,
        MAX(CASE WHEN museum_name = 'Cleveland Museum of Art' THEN total_artworks || ' works (' || unique_artists || ' artists)' END) AS cleveland,
        MAX(CASE WHEN museum_name = 'The Metropolitan Museum of Art' THEN total_artworks || ' works (' || unique_artists || ' artists)' END) AS met,
        SUM(total_artworks) AS global_total_artworks
    FROM MacroMuseumStats
    GROUP BY macro_region
)
SELECT
    macro_region,
    COALESCE(chicago, '0 works (0 artists)') AS chicago,
    COALESCE(cleveland, '0 works (0 artists)') AS cleveland,
    COALESCE(met, '0 works (0 artists)') AS met,
    global_total_artworks
FROM PivotedMacro
ORDER BY global_total_artworks DESC
LIMIT 10;


-- 2. Which artists have the highest number of artworks produced in countries different from their nationality?
SELECT
    a.artist_name,
    a.birth_date,
    a.death_date,
    nat_artist.country_name AS artist_birth_country,
    orig_art.country_name AS artwork_origin_country,
    COUNT(f.id_artwork) AS foreign_artworks_count
FROM fact_artworks f
JOIN dim_artist a ON f.id_artist = a.id_artist
JOIN dim_geography nat_artist ON a.id_nationality_country = nat_artist.id_country
JOIN dim_geography orig_art ON f.id_origin_country = orig_art.id_country
WHERE f.id_artist != 0
  AND a.id_nationality_country != 0
  AND f.id_origin_country != 0
  AND a.id_nationality_country != f.id_origin_country
  AND a.artist_name NOT IN ('Unknown', 'India', 'French')
  AND orig_art.country_name != 'Unknown'
GROUP BY
    a.artist_name,
    a.birth_date,
    a.death_date,
    nat_artist.country_name,
    orig_art.country_name
ORDER BY foreign_artworks_count DESC
LIMIT 15;


-- 3. For each historical period and macroregion, what is the predominant technique and most-used material?
WITH TechGeoEpochStats AS (
    SELECT
        m.historical_epoch,
        g.macro_region,
        t.technique_type,
        t.material_type,
        COUNT(f.id_artwork) AS total_artworks,
        ROW_NUMBER() OVER (
            PARTITION BY m.historical_epoch, g.macro_region
            ORDER BY COUNT(f.id_artwork) DESC
        ) AS rank_tech
    FROM fact_artworks f
    JOIN dim_technique t ON f.id_technique = t.id_technique
    JOIN dim_geography g ON f.id_origin_country = g.id_country
    JOIN dim_movement m ON f.id_movement = m.id_movement
    WHERE f.id_technique != 0
      AND f.id_origin_country != 0
      AND f.id_movement != 0
      AND m.historical_epoch IS NOT NULL
      AND g.macro_region IS NOT NULL
      AND t.technique_type != 'Unknown'
    GROUP BY m.historical_epoch, g.macro_region, t.technique_type, t.material_type
)
SELECT
    historical_epoch,
    macro_region,
    technique_type AS predominant_technique,
    material_type AS predominant_material,
    total_artworks
FROM TechGeoEpochStats
WHERE rank_tech = 1
ORDER BY historical_epoch, macro_region;


-- 4. Which techniques and materials have the highest production intensity (average area / average production years)?
-- Which are the most productive in terms of average area and average production years?
SELECT
    t.technique_type,
    t.material_type,
    ROUND(AVG(f.area_cm2), 2) AS average_area_cm2,
    -- If production_duration is 0, consider it 1 year for the average and index calculation
    ROUND(AVG(CASE WHEN f.production_duration = 0 THEN 1 ELSE f.production_duration END), 2) AS average_production_years,
    ROUND(
        AVG(f.area_cm2) / NULLIF(AVG(CASE WHEN f.production_duration = 0 THEN 1 ELSE f.production_duration END), 0),
        2
    ) AS production_intensity_index
FROM fact_artworks f
JOIN dim_technique t ON f.id_technique = t.id_technique
WHERE f.id_technique != 0
  AND f.area_cm2 IS NOT NULL
  AND f.production_duration IS NOT NULL
  -- Filter up to 25 years to exclude historical/dynastic ranges
  AND f.production_duration >= 0
  AND f.production_duration <= 25
  AND t.technique_type != 'Unknown Technique'
  AND t.material_type != 'Unknown Support'
GROUP BY t.technique_type, t.material_type
HAVING COUNT(f.id_artwork) >= 5
ORDER BY production_intensity_index DESC, average_area_cm2 DESC;


-- 5. Which artistic movements, together with their respective century, have the widest spread across macroregions and countries?
SELECT
    m.movement_name,
    dt.century,
    COUNT(DISTINCT g.macro_region) AS number_of_macroregions_involved,
    STRING_AGG(DISTINCT g.macro_region, ', ') AS macroregion_list,
    COUNT(DISTINCT g.country_name) AS number_of_countries_involved,
    STRING_AGG(DISTINCT g.country_name, ', ') AS country_list,
    COUNT(f.id_artwork) AS total_worldwide_artworks
FROM fact_artworks f
JOIN dim_movement m ON f.id_movement = m.id_movement
JOIN dim_time dt ON f.id_start_year = dt.id_year
JOIN dim_geography g ON f.id_origin_country = g.id_country
WHERE f.id_movement != 0
  AND f.id_origin_country != 0
  AND f.id_start_year != 0
  AND m.movement_name != 'Unknown'
  AND dt.century IS NOT NULL
  AND g.macro_region IS NOT NULL
  AND g.country_name IS NOT NULL
GROUP BY m.movement_name, dt.century
HAVING COUNT(f.id_artwork) >= 10
ORDER BY number_of_countries_involved DESC, total_worldwide_artworks DESC;


-- 6. How does artist productivity vary in relation to the age at which they started producing artworks?
SELECT
    CONCAT(FLOOR((f.id_start_year - a.birth_date) / 10) * 10, '-', FLOOR((f.id_start_year - a.birth_date) / 10) * 10 + 9) AS age_group,
    COUNT(f.id_artwork) AS total_artworks_analyzed,
    ROUND(AVG(f.area_cm2), 2) AS average_area_cm2,
    ROUND(AVG(CASE WHEN f.production_duration = 0 THEN 1 ELSE f.production_duration END), 2) AS average_production_years,
    -- Creation pace index: Years required per square meter (Years / Area in sqm)
    ROUND(
        (AVG(CASE WHEN f.production_duration = 0 THEN 1 ELSE f.production_duration END) / NULLIF(AVG(f.area_cm2), 0)) * 10000,
        2
    ) AS creation_pace_index
FROM fact_artworks f
JOIN dim_artist a ON f.id_artist = a.id_artist
WHERE f.id_artist != 0
  AND a.birth_date IS NOT NULL
  AND f.id_start_year != 0
  AND (f.id_start_year - a.birth_date) BETWEEN 10 AND 95
  AND f.production_duration >= 0
  AND f.production_duration <= 25
  AND f.area_cm2 IS NOT NULL
GROUP BY FLOOR((f.id_start_year - a.birth_date) / 10) * 10
HAVING COUNT(f.id_artwork) >= 10
ORDER BY FLOOR((f.id_start_year - a.birth_date) / 10) * 10 ASC;


-- 7. Which countries and macroregions have the highest artist production intensity in terms of average area per average production year?
SELECT
    g.country_name AS artist_country,
    g.macro_region,
    COUNT(f.id_artwork) AS total_artworks,
    ROUND(AVG(f.area_cm2), 2) AS average_area_cm2,
    ROUND(AVG(CASE WHEN f.production_duration = 0 THEN 1 ELSE f.production_duration END), 2) AS average_production_years,
    ROUND(
        AVG(f.area_cm2) / NULLIF(AVG(CASE WHEN f.production_duration = 0 THEN 1 ELSE f.production_duration END), 0),
        2
    ) AS production_intensity_index
FROM fact_artworks f
JOIN dim_artist a ON f.id_artist = a.id_artist
JOIN dim_geography g ON a.id_nationality_country = g.id_country
WHERE f.id_artist != 0
  AND a.id_nationality_country != 0
  AND f.area_cm2 IS NOT NULL
  AND f.production_duration IS NOT NULL
  AND f.production_duration >= 0
  AND f.production_duration <= 25
  AND g.country_name != 'Unknown'
GROUP BY g.country_name, g.macro_region
HAVING COUNT(f.id_artwork) >= 20
ORDER BY production_intensity_index DESC, average_area_cm2 DESC;

-- 8. How does the average artwork area vary by production decade for each museum?
WITH MuseumDecadeArea AS (
    SELECT
        mu.museum_name,
        dt.decade,
        ROUND(AVG(f.area_cm2), 2) AS average_area
    FROM fact_artworks f
    JOIN dim_time dt ON f.id_start_year = dt.id_year
    JOIN dim_museum mu ON f.id_museum = mu.id_museum
    WHERE dt.decade BETWEEN 1900 AND 1990
      AND f.id_start_year != 0
      AND f.area_cm2 IS NOT NULL
      AND mu.id_museum != 0
    GROUP BY mu.museum_name, dt.decade
)
SELECT
	museum_name AS museum,
    MAX(CASE WHEN decade = 1900 THEN average_area END) AS "1900-1909",
    MAX(CASE WHEN decade = 1910 THEN average_area END) AS "1910-1919",
    MAX(CASE WHEN decade = 1920 THEN average_area END) AS "1920-1929",
    MAX(CASE WHEN decade = 1930 THEN average_area END) AS "1930-1939",
    MAX(CASE WHEN decade = 1940 THEN average_area END) AS "1940-1949",
    MAX(CASE WHEN decade = 1950 THEN average_area END) AS "1950-1959",
    MAX(CASE WHEN decade = 1960 THEN average_area END) AS "1960-1969",
    MAX(CASE WHEN decade = 1970 THEN average_area END) AS "1970-1979",
    MAX(CASE WHEN decade = 1980 THEN average_area END) AS "1980-1989",
    MAX(CASE WHEN decade = 1990 THEN average_area END) AS "1990-1999"
FROM MuseumDecadeArea
GROUP BY museum_name
ORDER BY museum_name ASC;