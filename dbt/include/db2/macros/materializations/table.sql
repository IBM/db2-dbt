{% materialization table, adapter='db2' %}
  {%- set identifier = model['alias'] -%}
  {%- set old_relation = adapter.get_relation(database=database, schema=schema, identifier=identifier) -%}
  {%- set target_relation = api.Relation.create(identifier=identifier,
                                                schema=schema,
                                                database=database,
                                                type='table') -%}

  {{ run_hooks(pre_hooks) }}

  -- Drop the relation if it exists and we're not using incremental strategies
  {% if old_relation is not none %}
    {{ adapter.drop_relation(old_relation) }}
  {% endif %}

  -- Extract the final SELECT statement from the SQL if it has CTEs
  {% set model_sql = sql %}
  {% set sql_no_ctes = model_sql %}
  {% if model_sql.strip().upper().startswith('WITH') %}
    {% set final_select_pos = model_sql.upper().rfind('SELECT') %}
    {% if final_select_pos > 0 %}
      {% set sql_no_ctes = model_sql[final_select_pos:] %}
    {% endif %}
  {% endif %}

  -- Build the SQL for creating the table
  {% set build_sql %}
    create table {{ target_relation }}
    as (
      {{ sql_no_ctes }}
    ) with data
  {% endset %}

  -- Execute the SQL to create the table
  {% call statement('main') %}
    {{ build_sql }}
  {% endcall %}

  -- Log the created table for debugging
  {% call statement('log_table_creation') %}
    select 'Created table: ' || '{{ target_relation }}' as message from SYSIBM.SYSDUMMY1
  {% endcall %}

  -- Commit the transaction to ensure the table is persisted
  {% call statement('commit') %}
    commit
  {% endcall %}

  {{ run_hooks(post_hooks) }}

  {{ return({'relations': [target_relation]}) }}
{% endmaterialization %}

-- Made with Bob
