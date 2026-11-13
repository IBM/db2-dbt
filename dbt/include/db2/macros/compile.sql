{% macro db2__compile_sql(sql) %}
  {# Db2 supports CTEs natively, so the SQL is returned unchanged #}
  {{ return(sql) }}
{% endmacro %}
