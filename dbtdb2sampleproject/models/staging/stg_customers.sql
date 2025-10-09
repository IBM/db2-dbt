{{
  config(
    materialized = 'table'
    )
}}

-- DB2 doesn't handle CTEs well, so we'll use a simpler approach
select
    id as customer_id,
    first_name,
    last_name
from {{ source('sample_source','cust') }}
