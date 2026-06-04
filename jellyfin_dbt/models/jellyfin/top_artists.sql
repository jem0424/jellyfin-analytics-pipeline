SELECT
    artist,
    COUNT(*) as total_plays,
    COUNT(DISTINCT user_id) as unique_listeners,
    COUNT(DISTINCT item_id) as unique_tracks
FROM {{ source('public', 'raw_plays') }}
WHERE artist IS NOT NULL
GROUP BY artist
ORDER BY total_plays DESC
