{{ config(
    materialized='incremental',
    unique_key='order_id'
) }}

WITH source_data AS (
    SELECT
        order_id,
        customer_id,
        order_date,
        status
    FROM
        {{ ref('stg_orders') }}
)

SELECT
    order_id,
    customer_id,
    order_date,
    status
FROM
    source_data

{% if is_incremental() %}
    -- Only include rows where `order_date` is greater than the max date in the existing table
    WHERE order_date > (SELECT MAX(order_date) FROM {{ this }})
{% endif %}
