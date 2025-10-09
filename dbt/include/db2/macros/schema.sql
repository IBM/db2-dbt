{% macro db2__create_schema(relation) -%}
  {# Do nothing - assume schema already exists #}
  {% do return('') %}
{% endmacro %}
