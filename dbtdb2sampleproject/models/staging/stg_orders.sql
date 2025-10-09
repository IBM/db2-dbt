{{
  config(
    materialized = 'table'
    )
}}

-- DB2 doesn't handle CTEs well, so we'll use a simpler approach
select
    id as order_id,
    user_id as customer_id,
    order_date,
    status
from {{ source('sample_source','ordrs') }}
