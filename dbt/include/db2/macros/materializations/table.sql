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

  -- Build the SQL for creating the table (Db2 supports CTEs inside the fullselect)
  {% set build_sql %}
    create table {{ target_relation }}
    as (
      {{ sql }}
    ) WITH DATA
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
