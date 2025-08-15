SELECT id, statement_id, transaction_date, ABS(amount) as debit, cleaned_description, category
FROM {{ ref('silver_transactions') }}
WHERE amount < 0 