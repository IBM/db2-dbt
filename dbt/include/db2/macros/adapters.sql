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
  {# Return an empty list for now to get past this error #}
  {{ return([]) }}
{% endmacro %}

{% macro db2__list_relations_without_caching(schema_relation) %}
  {# Return an empty list for now to get past this error #}
  {{ return([]) }}
{% endmacro %}

{% macro db2__drop_schema(relation) -%}
  {%- call statement('drop_schema') -%}
    {{ exceptions.raise_compiler_error("dbt-ibm-db2 does not support drop_schema") }}
  {% endcall %}
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
          column_name,
          data_type,
          character_maximum_length,
          numeric_precision,
          numeric_scale
      from {{ relation.information_schema('columns') }}
      where table_name like '{{ relation.identifier }}'
        {% if relation.schema %}
        and table_schema like '{{ relation.schema }}'
        {% endif %}
      order by ordinal_position
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
