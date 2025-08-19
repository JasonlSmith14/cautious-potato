WITH annotated AS (
SELECT 
    *,
    ROW_NUMBER() OVER(PARTITION BY statement_id, transaction_date, description, amount)
FROM 
    {{ ref('bronze_transactions') }}
)

SELECT DISTINCT ON (transaction_date, description, amount, row_number)
    id,
    statement_id, 
    transaction_date,
    amount, 
    cleaned_description,
    description_embedding,
    category,
    balance
FROM annotated
ORDER BY transaction_date, description, row_number, amount, id ASC
