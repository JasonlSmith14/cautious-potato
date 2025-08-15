SELECT
  category,
  SUM(debit) AS total_amount
FROM {{ ref('gold_debits') }}
GROUP BY category
ORDER BY category