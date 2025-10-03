{{
  config(
    materialized = 'ephemeral'
    )
}}

with source as (
    {#-
    We can either use {{ ref('raw_orders') }} , it would refer the table created by the seeds file or we can also use
    {{ source('sample_source','ordrs') }} and it would fetch data from table ORDERS in our schema.
    #}
    select * from {{ source('sample_source','ordrs') }}
),

renamed as (

    select
        id as order_id,
        user_id as customer_id,
        order_date,
        status

    from source

)

select * from renamed
