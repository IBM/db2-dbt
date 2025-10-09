-- DB2 doesn't handle CTEs well, so we'll use a simpler approach
select
    c.customer_id,
    c.first_name,
    c.last_name,
    min(o.order_date) as first_order,
    max(o.order_date) as most_recent_order,
    count(o.order_id) as number_of_orders,
    sum(p.amount) as customer_lifetime_value
from "TESTDB"."NEWUSER"."stg_customers" c
left join "TESTDB"."NEWUSER"."stg_orders" o
    on c.customer_id = o.customer_id
left join "TESTDB"."NEWUSER"."stg_payments" p
    on o.order_id = p.order_id
group by
    c.customer_id,
    c.first_name,
    c.last_name
