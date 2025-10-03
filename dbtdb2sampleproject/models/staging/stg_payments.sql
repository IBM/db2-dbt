{{
  config(
    materialized = 'ephemeral'
    )
}}

with source as ( 
    {#-
    We can either use {{ ref('raw_payments') }} , it would refer the table created by the seeds file or we can also use
    {{ source('sample_source','payments') }} and it would fetch data from table PAYMENTS in our schema.
    #}
    select * from {{ source('sample_source','payments') }}

),

renamed as (

    select
        id as payment_id,
        order_id,
        payment_method,

        -- `amount` is currently stored in cents, so we convert it to dollars
        amount / 100 as amount

    from source

)

select * from renamed
