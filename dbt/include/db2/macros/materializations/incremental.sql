{% materialization incremental, adapter='db2' %}
  {% set unique_key = config.get('unique_key') %}
  {% set full_refresh_mode = flags.FULL_REFRESH %}
  {% set target_relation = this.incorporate(type='table') %}
  {% set existing_relation = load_relation(this) %}
  {% set tmp_relation = make_temp_relation(this) %}

  {{ run_hooks(pre_hooks) }}

  -- Extract the final SELECT statement from the SQL if it has CTEs
  {% set model_sql = sql %}
  {% set sql_no_ctes = model_sql %}
  {% if model_sql.strip().upper().startswith('WITH') %}
    {% set final_select_pos = model_sql.upper().rfind('SELECT') %}
    {% if final_select_pos > 0 %}
      {% set sql_no_ctes = model_sql[final_select_pos:] %}
    {% endif %}
  {% endif %}

  {% if existing_relation is none %}
    -- Create the table if it doesn't exist
    {% set build_sql %}
      create table {{ target_relation }}
      as (
        {{ sql_no_ctes }}
      ) with data
    {% endset %}
  {% elif full_refresh_mode %}
    -- Drop and recreate the table if full refresh
    {% do adapter.drop_relation(target_relation) %}
    {% set build_sql %}
      create table {{ target_relation }}
      as (
        {{ sql_no_ctes }}
      ) with data
    {% endset %}
  {% else %}
    -- Create a temporary table with the new data
    {% do adapter.drop_relation(tmp_relation) if tmp_relation is not none %}
    {% set tmp_table_sql %}
      create table {{ tmp_relation }}
      as (
        {{ sql_no_ctes }}
      ) with data
    {% endset %}
    {% do run_query(tmp_table_sql) %}

    -- Use delete+insert strategy for incremental updates
    {% set dest_columns = adapter.get_columns_in_relation(target_relation) %}
    {% set dest_cols_csv = dest_columns | map(attribute='quoted') | join(', ') %}

    {% if unique_key %}
      {% if unique_key is sequence and unique_key is not string %}
        {% set unique_key_match %}
          {% for key in unique_key %}
            {{ target_relation }}.{{ key }} = {{ tmp_relation }}.{{ key }}
            {% if not loop.last %} and {% endif %}
          {% endfor %}
        {% endset %}
      {% else %}
        {% set unique_key_match %}
          {{ target_relation }}.{{ unique_key }} = {{ tmp_relation }}.{{ unique_key }}
        {% endset %}
      {% endif %}

      {% set build_sql %}
        -- Delete records that will be updated
        delete from {{ target_relation }}
        where exists (
          select 1 from {{ tmp_relation }}
          where {{ unique_key_match }}
        );
        
        -- Insert new/updated records
        insert into {{ target_relation }} ({{ dest_cols_csv }})
        select {{ dest_cols_csv }}
        from {{ tmp_relation }};
      {% endset %}
    {% else %}
      {% set build_sql %}
        -- Insert all records (no unique key specified)
        insert into {{ target_relation }} ({{ dest_cols_csv }})
        select {{ dest_cols_csv }}
        from {{ tmp_relation }};
      {% endset %}
    {% endif %}
  {% endif %}

  {% call statement('main') %}
    {{ build_sql }}
  {% endcall %}

  {{ run_hooks(post_hooks) }}

  {{ return({'relations': [target_relation]}) }}
{% endmaterialization %}

-- Made with Bob
