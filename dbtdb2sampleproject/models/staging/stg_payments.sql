{{
  config(
    materialized = 'table'
    )
}}

-- DB2 doesn't handle CTEs well, so we'll use a simpler approach
select
    id as payment_id,
    order_id,
    payment_method,
    -- `amount` is currently stored in cents, so we convert it to dollars
    amount / 100 as amount
from {{ source('sample_source','payments') }}
