SELECT
    DATE(played_at) as play_date,
    username,
    COUNT(*) as tracks_played,
    SUM(play_duration) as total_seconds,
    ROUND(SUM(play_duration) / 3600.0, 2) as total_hours
FROM {{ source('public', 'raw_plays') }}
GROUP BY DATE(played_at), username
ORDER BY play_date DESC
