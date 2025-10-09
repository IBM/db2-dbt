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

  -- Extract the final SELECT statement from the SQL if it has CTEs
  {% set model_sql = sql %}
  {% set sql_no_ctes = model_sql %}
  {% if model_sql.strip().upper().startswith('WITH') %}
    {% set final_select_pos = model_sql.upper().rfind('SELECT') %}
    {% if final_select_pos > 0 %}
      {% set sql_no_ctes = model_sql[final_select_pos:] %}
    {% endif %}
  {% endif %}

  -- Build the SQL for creating the view
  {% set build_sql %}
    create view {{ target_relation }}
    as
      {{ sql_no_ctes }}
  {% endset %}

  -- Execute the SQL to create the view
  {% call statement('main') %}
    {{ build_sql }}
  {% endcall %}

  {{ run_hooks(post_hooks) }}

  {{ return({'relations': [target_relation]}) }}
{% endmaterialization %}

-- Made with Bob
