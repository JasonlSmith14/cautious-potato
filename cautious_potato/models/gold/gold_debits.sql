SELECT id, statement_id, transaction_date, ABS(amount) as debit, cleaned_description, description_embedding, category
FROM {{ ref('silver_transactions') }}
WHERE amount < 0 