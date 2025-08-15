WITH annotated AS (
SELECT
  EXTRACT(YEAR FROM transaction_date) AS year,
  TRIM(TO_CHAR(transaction_date, 'Month')) AS month,
  SUM(credit) AS total_amount
FROM {{ ref('gold_credits') }}
GROUP BY year, month
)

SELECT * 
FROM annotated
ORDER BY TO_DATE(year || ' ' || month, 'YYYY Month')