-- 创建 baduserdetail 视图
CREATE OR REPLACE VIEW baduserdetail AS
WITH badmain_with_year AS (
    SELECT
        username,
        CAST(SUBSTRING(Date, 1, 4) AS UNSIGNED) AS year,
        CAST(views AS UNSIGNED) AS views,
        CAST(likes AS UNSIGNED) AS likes,
        CAST(coins AS UNSIGNED) AS coins,
        CAST(collects AS UNSIGNED) AS collects,
        part
    FROM badmain
),
aggregated AS (
    SELECT
        ub.username,
        CAST(ub.year AS UNSIGNED) AS year,
        SUM(b.views) AS views,
        SUM(b.likes) AS likes,
        SUM(b.coins) AS coins,
        SUM(b.collects) AS collects
    FROM userbad ub
    LEFT JOIN badmain_with_year b
        ON ub.username = b.username AND b.year <= CAST(ub.year AS UNSIGNED)
    GROUP BY ub.username, ub.year
),
part_agg AS (
    SELECT
        ub.username,
        CAST(ub.year AS UNSIGNED) AS year,
        b.part,
        COUNT(*) AS part_count,
        ROW_NUMBER() OVER (PARTITION BY ub.username, ub.year ORDER BY COUNT(*) DESC, b.part ASC) AS rn
    FROM userbad ub
    LEFT JOIN badmain_with_year b
        ON ub.username = b.username AND b.year <= CAST(ub.year AS UNSIGNED)
    GROUP BY ub.username, ub.year, b.part
)
SELECT
    a.username,
    CAST(ub.fans AS UNSIGNED) AS fans,
    a.year,
    a.views,
    a.likes,
    a.coins,
    a.collects,
    p.part
FROM aggregated a
JOIN userbad ub
    ON a.username = ub.username AND a.year = CAST(ub.year AS UNSIGNED)
LEFT JOIN (
    SELECT username, year, part
    FROM part_agg
    WHERE rn = 1
) p
    ON a.username = p.username AND a.year = p.year;
