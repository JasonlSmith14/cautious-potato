WITH annotated AS (
SELECT 
    *,
    ROW_NUMBER() OVER(PARTITION BY statement_id, transaction_date, amount)
FROM 
    {{ ref('bronze_transactions') }}
)

SELECT DISTINCT ON (transaction_date, amount, row_number)
    id,
    statement_id, 
    transaction_date,
    amount, 
    cleaned_description,
    description_embedding,
    category,
    balance
FROM annotated
ORDER BY transaction_date, row_number, amount, id ASC
