{% macro db2__render_sql(sql, model, add_extras) %}
  {# Db2 supports CTEs natively, so the rendered SQL is returned unchanged #}
  {{ return(default__render_sql(sql, model, add_extras)) }}
{% endmacro %}
