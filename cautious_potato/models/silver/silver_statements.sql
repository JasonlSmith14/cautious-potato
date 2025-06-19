-- We do not remove duplicates here in the chance that you could have generated two statements on the same day
-- For example, one in the morning and one in the evening
-- We handle deduplication at a transaction level

SELECT DISTINCT
    id,
    start_date,
    end_date,
    end_date - start_date AS duration
FROM {{ ref('bronze_statements') }}
