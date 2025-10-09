{{ config(
    materialized='incremental',
    unique_key='order_id'
) }}

-- DB2 doesn't handle CTEs well, so we'll use a simpler approach
SELECT
    order_id,
    customer_id,
    order_date,
    status
FROM
    "TESTDB"."NEWUSER"."stg_orders"

{% if is_incremental() %}
    -- Only include rows where `order_date` is greater than the max date in the existing table
    WHERE order_date > (SELECT MAX(order_date) FROM {{ this }})
{% endif %}
