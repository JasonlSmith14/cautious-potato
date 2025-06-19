WITH base AS (
    SELECT
        DATE_TRUNC('month', transaction_date) AS month,
        category,
        amount
    FROM {{ ref('silver_debits') }}
)

SELECT
    month,
    category,
    SUM(amount) AS total_spent,
    COUNT(*) AS transactions
FROM base
GROUP BY month, category
ORDER BY month
