SELECT
  category,
  EXTRACT(YEAR FROM transaction_date)  AS year,
  TO_CHAR(transaction_date, 'Month') AS month,
  SUM(credit) AS total_amount
FROM {{ ref('gold_credits') }}
GROUP BY category, year, month

