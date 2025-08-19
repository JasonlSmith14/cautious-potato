SELECT 
    transactions.id,
    statement_id, 
    transaction_date,
    amount,
    description,
    description_embedding,
    cleaned_description,
    category,
    reasoning,
    balance
FROM transactions
JOIN {{ ref('bronze_categories') }} AS bronze_categories ON transactions.category_id = bronze_categories.id