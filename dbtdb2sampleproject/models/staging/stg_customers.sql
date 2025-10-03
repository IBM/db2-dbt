{{
  config(
    materialized = 'table'
    )
}}

with source as (
    {#-
    We can either use {{ ref('raw_customers') }} , it would refer the table created by the seeds file or we can also use
    {{ source('sample_source','cust') }} and it would fetch data from table CUSTOMERS in our schema.
    #}
    select * from {{ source('sample_source','cust') }}
),

renamed as (

    select
        id as customer_id,
        first_name,
        last_name

    from source

)

select * from renamed
