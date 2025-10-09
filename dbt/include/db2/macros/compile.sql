{% macro db2__compile_sql(sql) %}
  {# This macro is used by dbt to compile SQL #}
  {# We need to override it to handle DB2's limitations with CTEs #}
  
  {# Extract the final SELECT statement from the SQL if it has CTEs #}
  {% set sql_no_ctes = sql %}
  {% if sql.strip().upper().startswith('WITH') %}
    {% set final_select_pos = sql.upper().rfind('SELECT') %}
    {% if final_select_pos > 0 %}
      {% set sql_no_ctes = sql[final_select_pos:] %}
    {% endif %}
  {% endif %}
  
  {# Return the simplified SQL #}
  {{ return(sql_no_ctes) }}
{% endmacro %}

-- Made with Bob
