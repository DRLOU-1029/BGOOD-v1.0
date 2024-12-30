-- 创建 userdetail 视图
CREATE OR REPLACE VIEW userdetail AS
WITH main_with_year AS (
    SELECT
        username,
        CAST(SUBSTRING(Date, 1, 4) AS UNSIGNED) AS year,
        CAST(views AS UNSIGNED) AS views,
        CAST(likes AS UNSIGNED) AS likes,
        CAST(coins AS UNSIGNED) AS coins,
        CAST(collects AS UNSIGNED) AS collects,
        part
    FROM main
),
aggregated AS (
    SELECT
        ug.username,
        CAST(ug.year AS UNSIGNED) AS year,
        SUM(m.views) AS views,
        SUM(m.likes) AS likes,
        SUM(m.coins) AS coins,
        SUM(m.collects) AS collects
    FROM usergood ug
    LEFT JOIN main_with_year m
        ON ug.username = m.username AND m.year <= CAST(ug.year AS UNSIGNED)
    GROUP BY ug.username, ug.year
),
part_agg AS (
    SELECT
        ug.username,
        CAST(ug.year AS UNSIGNED) AS year,
        m.part,
        COUNT(*) AS part_count,
        ROW_NUMBER() OVER (PARTITION BY ug.username, ug.year ORDER BY COUNT(*) DESC, m.part ASC) AS rn
    FROM usergood ug
    LEFT JOIN main_with_year m
        ON ug.username = m.username AND m.year <= CAST(ug.year AS UNSIGNED)
    GROUP BY ug.username, ug.year, m.part
)
SELECT
    a.username,
    CAST(ug.fans AS UNSIGNED) AS fans,
    a.year,
    a.views,
    a.likes,
    a.coins,
    a.collects,
    p.part
FROM aggregated a
JOIN usergood ug
    ON a.username = ug.username AND a.year = CAST(ug.year AS UNSIGNED)
LEFT JOIN (
    SELECT username, year, part
    FROM part_agg
    WHERE rn = 1
) p
    ON a.username = p.username AND a.year = p.year;
