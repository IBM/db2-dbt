{% macro db2__create_schema(relation) -%}
  {%- set schema_name = relation.without_identifier() -%}
  
  {# Check if schema exists #}
  {% set check_schema_sql %}
    SELECT COUNT(*) as schema_exists
    FROM SYSCAT.SCHEMATA
    WHERE SCHEMANAME = '{{ schema_name.schema.upper() }}'
  {% endset %}
  
  {% set results = run_query(check_schema_sql) %}
  
  {% if execute %}
    {% set schema_exists = results.columns[0].values()[0] %}
    
    {% if schema_exists == 0 %}
      {%- call statement('create_schema') -%}
        CREATE SCHEMA {{ schema_name }}
      {%- endcall -%}
      {{ log("Created schema " ~ schema_name, info=True) }}
    {% else %}
      {{ log("Schema " ~ schema_name ~ " already exists, skipping creation", info=True) }}
    {% endif %}
  {% endif %}
{% endmacro %}

{% macro db2__drop_schema(relation) -%}
  {%- set schema_name = relation.without_identifier() -%}
  
  {# Check if schema exists before dropping #}
  {% set check_schema_sql %}
    SELECT COUNT(*) as schema_exists
    FROM SYSCAT.SCHEMATA
    WHERE SCHEMANAME = '{{ schema_name.schema.upper() }}'
  {% endset %}
  
  {% set results = run_query(check_schema_sql) %}
  
  {% if execute %}
    {% set schema_exists = results.columns[0].values()[0] %}
    
    {% if schema_exists > 0 %}
      {%- call statement('drop_schema') -%}
        DROP SCHEMA {{ schema_name }} RESTRICT
      {%- endcall -%}
      {{ log("Dropped schema " ~ schema_name, info=True) }}
    {% else %}
      {{ log("Schema " ~ schema_name ~ " does not exist, skipping drop", info=True) }}
    {% endif %}
  {% endif %}
{% endmacro %}
