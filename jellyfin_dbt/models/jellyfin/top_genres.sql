SELECT
    i.genre,
    COUNT(p.id) as total_plays,
    COUNT(DISTINCT p.artist) as unique_artists
FROM {{ source('public', 'raw_plays') }} p
JOIN {{ source('public', 'raw_items') }} i
    ON p.item_id = i.item_id
WHERE i.genre IS NOT NULL
GROUP BY i.genre
ORDER BY total_plays DESC
