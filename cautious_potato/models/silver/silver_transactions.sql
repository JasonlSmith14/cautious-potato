-- Duplicate transactions can be expected under the same statement_id
-- An example: Fees for payments made when receiving your salary
-- But, we should not allow duplicate transactions across different statement_ids
-- This would then mean we processed the same transaction more than once which could be possible in over-lapping windows in bank staments
-- An example, 3-months vs 6-months

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
    category,
    balance
FROM annotated
ORDER BY transaction_date, description, row_number, amount, id ASC
