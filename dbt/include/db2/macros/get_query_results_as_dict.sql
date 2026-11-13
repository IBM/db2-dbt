{% macro db2__get_query_results_as_dict(sql) %}
  {# Db2 supports CTEs natively, so the SQL is passed through unchanged #}
  {{ return(default__get_query_results_as_dict(sql)) }}
{% endmacro %}
