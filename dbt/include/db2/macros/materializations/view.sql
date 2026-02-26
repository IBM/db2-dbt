{% materialization view, adapter='db2' %}
  {%- set identifier = model['alias'] -%}
  {%- set old_relation = adapter.get_relation(database=database, schema=schema, identifier=identifier) -%}
  {%- set target_relation = api.Relation.create(identifier=identifier,
                                                schema=schema,
                                                database=database,
                                                type='view') -%}

  {{ run_hooks(pre_hooks) }}

  -- Drop the relation if it exists
  {% if old_relation is not none %}
    {{ adapter.drop_relation(old_relation) }}
  {% endif %}

  -- Build the SQL for creating the view with full SQL (including CTEs)
  {% set build_sql %}
    create view {{ target_relation }}
    as
      {{ sql }}
  {% endset %}

  -- Execute the SQL to create the view
  {% call statement('main') %}
    {{ build_sql }}
  {% endcall %}

  -- Commit the transaction to ensure view is persisted in DB2
  {% call statement('commit_view', auto_begin=False) %}
    COMMIT
  {% endcall %}

  {{ run_hooks(post_hooks) }}

  {{ return({'relations': [target_relation]}) }}
{% endmaterialization %}

-- Made with Bob
