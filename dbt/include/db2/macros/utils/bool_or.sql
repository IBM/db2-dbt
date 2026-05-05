{% macro db2__bool_or(condition) %}
    cast(cast(max(case when {{ condition }} then 1 else 0 end) as char(1)) as boolean)
{% endmacro %}
