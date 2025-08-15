SELECT
  category,
  EXTRACT(YEAR FROM transaction_date)  AS year,
  SUM(debit) AS total_amount
FROM {{ ref('gold_debits') }}
GROUP BY category, year
ORDER BY year, category