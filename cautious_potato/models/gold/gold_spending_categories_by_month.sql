WITH annotated AS (
SELECT
  category,
  EXTRACT(YEAR FROM transaction_date)  AS year,
  TO_CHAR(transaction_date, 'Month') AS month,
  SUM(debit) AS total_amount
FROM {{ ref('gold_debits') }}
GROUP BY category, year, month
)

SELECT *
FROM annotated
ORDER BY TO_DATE(year || ' ' || month, 'YYYY Month'), category