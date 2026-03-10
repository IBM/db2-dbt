{% macro list_tables(schema) %}
  {{ log("Starting list_tables macro with schema: " ~ schema, info=True) }}
  
  {% set query %}
    select
      tabname as table_name,
      tabschema as schema_name,
      type as table_type,
      create_time
    from syscat.tables
    where tabschema = 'NEWUSER'
    order by create_time desc
  {% endset %}
  
  {{ log("Executing query: " ~ query, info=True) }}
  
  {% set results = run_query(query) %}
  
  {{ log("Query executed. Results count: " ~ results|length, info=True) }}
  
  {% if execute %}
    {% if results|length > 0 %}
      {{ log("All tables in NEWUSER schema:", info=True) }}
      {% for row in results %}
        {% set table_name = row[0] %}
        {% set schema_name = row[1] %}
        {% set table_type = row[2] %}
        {% set create_time = row[3] %}
        {{ log("Table: " ~ schema_name ~ "." ~ table_name ~ " (Type: " ~ table_type ~ ", Created: " ~ create_time ~ ")", info=True) }}
      {% endfor %}
    {% else %}
      {{ log("No tables found in NEWUSER schema", info=True) }}
    {% endif %}
  {% endif %}
  
  {% set query %}
    select
      viewname as view_name,
      viewschema as schema_name,
      'V' as view_type
    from syscat.views
    where viewschema = 'NEWUSER'
  {% endset %}
  
  {{ log("Executing query: " ~ query, info=True) }}
  
  {% set results = run_query(query) %}
  
  {{ log("Query executed. Results count: " ~ results|length, info=True) }}
  
  {% if execute %}
    {% if results|length > 0 %}
      {{ log("All views in NEWUSER schema:", info=True) }}
      {% for row in results %}
        {% set view_name = row[0] %}
        {% set schema_name = row[1] %}
        {% set view_type = row[2] %}
        {{ log("View: " ~ schema_name ~ "." ~ view_name ~ " (Type: " ~ view_type ~ ")", info=True) }}
      {% endfor %}
    {% else %}
      {{ log("No views found in NEWUSER schema", info=True) }}
    {% endif %}
  {% endif %}
{% endmacro %}
