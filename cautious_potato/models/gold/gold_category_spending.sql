SELECT 
    SUM(amount) AS total_spent, 
    COUNT(*) AS transactions, 
    category
FROM {{ ref('silver_transactions') }}
GROUP BY category