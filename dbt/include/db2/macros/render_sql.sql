{% macro db2__render_sql(sql, model, add_extras) %}
  {# This macro is used by dbt to render SQL #}
  {# We need to override it to handle Db2s limitations with CTEs #}
  
  {# Call the default implementation to get the rendered SQL #}
  {% set rendered_sql = default__render_sql(sql, model, add_extras) %}
  
  {# Extract the final SELECT statement from the SQL if it has CTEs #}
  {% set sql_no_ctes = rendered_sql %}
  {% if rendered_sql.strip().upper().startswith('WITH') %}
    {% set final_select_pos = rendered_sql.upper().rfind('SELECT') %}
    {% if final_select_pos > 0 %}
      {% set sql_no_ctes = rendered_sql[final_select_pos:] %}
    {% endif %}
  {% endif %}
  
  {# Return the simplified SQL #}
  {{ return(sql_no_ctes) }}
{% endmacro %}
