{% macro db2__get_query_results_as_dict(sql) %}
  {# This macro is used by dbt to get query results as a dictionary #}
  {# We need to override it to handle DB2s limitations with CTEs #}
  
  {# Extract the final SELECT statement from the SQL if it has CTEs #}
  {% set sql_no_ctes = sql %}
  {% if sql.strip().upper().startswith('WITH') %}
    {% set final_select_pos = sql.upper().rfind('SELECT') %}
    {% if final_select_pos > 0 %}
      {% set sql_no_ctes = sql[final_select_pos:] %}
    {% endif %}
  {% endif %}
  
  {# Call the default implementation with the simplified SQL #}
  {{ return(default__get_query_results_as_dict(sql_no_ctes)) }}
{% endmacro %}
