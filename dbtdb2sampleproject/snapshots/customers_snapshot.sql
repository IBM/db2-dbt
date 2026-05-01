{% snapshot customers_snapshot %}

{{
    config(
        target_schema='sampleschema',
        unique_key='customer_id',
        strategy='check',
        check_cols=['first_name', 'last_name']
    )
}}

SELECT
    customer_id,
    first_name,
    last_name
FROM
    {{ ref('stg_customers') }}

{% endsnapshot %}
