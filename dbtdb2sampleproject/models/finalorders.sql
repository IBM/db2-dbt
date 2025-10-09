{% set payment_methods = ['credit_card', 'coupon', 'bank_transfer', 'gift_card'] %}

-- DB2 doesn't handle CTEs well, so we'll use a simpler approach
select
    o.order_id,
    o.customer_id,
    o.order_date,
    o.status,

    {% for payment_method in payment_methods -%}
    sum(case when p.payment_method = '{{ payment_method }}' then p.amount else 0 end) as {{ payment_method }}_amount,
    {% endfor -%}

    sum(p.amount) as amount

from "TESTDB"."NEWUSER"."stg_orders" o
left join "TESTDB"."NEWUSER"."stg_payments" p
    on o.order_id = p.order_id
group by
    o.order_id,
    o.customer_id,
    o.order_date,
    o.status
