{% macro dist(dist) %}
  {%- if dist is not none -%}
      {%- if dist is string -%}
        {%- if dist in ['random'] -%}
          distribute on {{ dist }}
        {%- else -%}
          distribute on ({{ dist }})
        {%- endif -%}
      {%- else -%}
        distribute on (
          {%- for item in dist -%}
            {{ item }}
            {%- if not loop.last -%},{%- endif -%}
          {%- endfor -%}
        )  
      {%- endif -%}
  {%- endif -%}
{%- endmacro -%}

{% macro create_table_with_constraints(relation, sql, _dist) %}
    {%- set _dist = config.get('dist') -%}
    create table
    {{ relation }}
    {{ get_assert_columns_equivalent(sql) }}
    {{ get_table_columns_and_constraints() }}
    {%- set sql = get_select_subquery(sql) %}
    {{ dist(_dist) }}
    ;

    {# DB2 does not support WITH clauses in INSERT statements #}
    {# Extract the final SELECT statement from the SQL #}
    {% set sql_no_ctes = sql %}
    {% if sql.strip().upper().startswith('WITH') %}
      {# This is a very simple approach - for complex CTEs, a more sophisticated parser would be needed #}
      {% set final_select_pos = sql.upper().rfind('SELECT') %}
      {% if final_select_pos > 0 %}
        {% set sql_no_ctes = sql[final_select_pos:] %}
      {% endif %}
    {% endif %}

    insert into {{ relation }}
    {{ sql_no_ctes }};
{% endmacro %}

{% macro create_table_no_constraints(temporary, relation, sql, _dist) %}
    {# DB2 does not support WITH clauses in CREATE TABLE AS statements #}
    {# Extract the final SELECT statement from the SQL #}
    {% set sql_no_ctes = sql %}
    {% if sql.strip().upper().startswith('WITH') %}
      {# This is a very simple approach - for complex CTEs, a more sophisticated parser would be needed #}
      {% set final_select_pos = sql.upper().rfind('SELECT') %}
      {% if final_select_pos > 0 %}
        {% set sql_no_ctes = sql[final_select_pos:] %}
      {% endif %}
    {% endif %}
    
    create {% if temporary -%}temporary{%- endif %} table
    {{ relation }}
    as (
        {{ sql_no_ctes }}
    )
    {{ dist(_dist) }}
    ;
{% endmacro %}

{% macro db2__create_table_as(temporary, relation, sql) -%}
  {%- set sql_header = config.get('sql_header', none) -%}
  {%- set _dist = config.get('dist') -%}
  {{ sql_header if sql_header is not none }}

  {% set contract_config = config.get('contract') %}
  {% if contract_config.enforced and (not temporary) %}
    {{ create_table_with_constraints(relation, sql, _dist) }}
  {% else %}
    {{ create_table_no_constraints(temporary, relation, sql, _dist) }}
  {% endif %}
{%- endmacro %}

{% macro db2__list_schemas(database) -%}
  {% call statement('list_schemas', fetch_result=True, auto_begin=False) %}
    SELECT SCHEMANAME as name
    FROM SYSCAT.SCHEMATA
    WHERE SCHEMANAME NOT LIKE 'SYS%'
      AND SCHEMANAME NOT IN ('NULLID', 'SQLJ', 'ERRORSCHEMA')
    ORDER BY SCHEMANAME
  {% endcall %}
  {{ return(load_result('list_schemas').table) }}
{% endmacro %}

{% macro db2__list_relations_without_caching(schema_relation) %}
  {% call statement('list_relations_without_caching', fetch_result=True) -%}
    SELECT
      CURRENT SERVER as database,
      TABSCHEMA as schema,
      TABNAME as name,
      CASE TYPE
        WHEN 'T' THEN 'table'
        WHEN 'V' THEN 'view'
        ELSE 'table'
      END as type
    FROM SYSCAT.TABLES
    WHERE TABSCHEMA = '{{ schema_relation.schema | upper }}'
      AND TYPE IN ('T', 'V')
    ORDER BY TABNAME
  {%- endcall %}
  {{ return(load_result('list_relations_without_caching').table) }}
{% endmacro %}

{% macro db2__drop_relation(relation) -%}
  {% call statement('drop_relation', auto_begin=False) -%}
    {% if relation.type == 'view' %}
        drop {{ relation.type }} {{ relation }}
    {% else %}
        drop {{ relation.type }} {{ relation }} if exists
    {% endif %}
  {%- endcall %}
{% endmacro %}

{% macro db2__rename_relation(from_relation, to_relation) -%}
  {% call statement('rename_relation') -%}
    alter {{ from_relation.type }} {{ from_relation }} rename to {{ to_relation }}
  {%- endcall %}
{% endmacro %}

{% macro db2__get_columns_in_relation(relation) -%}
  {% call statement('get_columns_in_relation', fetch_result=True) %}
      select
          COLNAME as column_name,
          TYPENAME as data_type,
          LENGTH as character_maximum_length,
          LENGTH as numeric_precision,
          SCALE as numeric_scale
      from SYSCAT.COLUMNS
      where TABNAME = '{{ relation.identifier | upper }}'
        {% if relation.schema %}
        and TABSCHEMA = '{{ relation.schema | upper }}'
        {% endif %}
      order by COLNO
  {% endcall %}
  {% set table = load_result('get_columns_in_relation').table %}
  {{ return(sql_convert_columns_in_relation(table)) }}
{% endmacro %}

{% macro db2__alter_relation_comment(relation, comment) %}
  {% set escaped_comment = db2_escape_comment(comment) %}
  comment on {{ relation.type }} {{ relation }} is {{ escaped_comment }};
{% endmacro %}

{% macro db2__alter_column_comment(relation, column_dict) %}
  {% set existing_columns = adapter.get_columns_in_relation(relation) | map(attribute="name") | list %}
  {% for column_name in column_dict if (column_name if column_dict[column_name]['quote'] else column_name | upper in existing_columns) %}
    {% set comment = column_dict[column_name]['description'] %}
    {% set escaped_comment = db2_escape_comment(comment) %}
    comment on column {{ relation }}.{{ adapter.quote(column_name) if column_dict[column_name]['quote'] else column_name }} is {{ escaped_comment }};
  {% endfor %}
{% endmacro %}

{% macro db2_escape_comment(comment) -%}
  {% if comment is not string %}
    {% do exceptions.raise_compiler_error('cannot escape a non-string: ' ~ comment) %}
  {% endif %}
  '{{ comment | replace("'", "''")}}'
{%- endmacro %}
