SELECT *
FROM {{ ref('silver_transactions') }}
WHERE amount < 0