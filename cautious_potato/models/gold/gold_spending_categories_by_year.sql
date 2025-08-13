SELECT
  category,
  EXTRACT(YEAR FROM transaction_date)  AS year,
  SUM(credit) AS total_amount
FROM {{ ref('gold_credits') }}
GROUP BY category, year
