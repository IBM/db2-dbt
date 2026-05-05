{% macro db2__snapshot_hash_arguments(args) -%}
    lower(
      rawtohex(
        hash(
          coalesce(
            cast(
              {%- for arg in args -%}
                coalesce(cast({{ arg }} as varchar(255)), '')
                {% if not loop.last %} || '|' || {% endif %}
              {%- endfor -%}
            as {{ type_string() }}),
          '')
        )
      )
    )
{%- endmacro %}
{% macro db2__build_snapshot_staging_table(strategy, sql, target_relation) %}
    {% set tmp_relation = make_temp_relation(target_relation) %}
    {% set select = snapshot_staging_table(strategy, sql, target_relation) %}

    {# Drop temp table if it exists using adapter method #}
    {% set tmp_relation_exists = load_relation(tmp_relation) %}
    {% if tmp_relation_exists is not none %}
        {% do adapter.drop_relation(tmp_relation) %}
    {% endif %}

    {% call statement('build_snapshot_staging_relation') %}
        {{ create_table_as(False, tmp_relation, select) }}
    {% endcall %}

    {% do return(tmp_relation) %}
{% endmacro %}


{% macro db2__snapshot_merge_sql(target, source, insert_cols) -%}
    
    {%- if insert_cols | length == 0 -%}
        {{ exceptions.raise_compiler_error("insert_cols is empty — column introspection failed. Check Db2 type mapping in adapter.") }}
    {%- endif -%}
    
    {%- set insert_cols_csv = insert_cols | join(', ') -%}

    {# Deduplicate source to avoid SQL0788N error in DB2 #}
    merge into {{ target }} as DBT_INTERNAL_DEST
    using (
        select * from (
            select *,
                   row_number() over (
                       partition by dbt_scd_id
                       order by dbt_updated_at desc
                   ) as rn
            from {{ source }}
        ) where rn = 1
    ) as DBT_INTERNAL_SOURCE
    on cast(DBT_INTERNAL_SOURCE.dbt_scd_id as {{ type_string() }}) = cast(DBT_INTERNAL_DEST.dbt_scd_id as {{ type_string() }})
    when matched
      and cast(DBT_INTERNAL_SOURCE.dbt_change_type as {{ type_string() }}) in (cast('update' as {{ type_string() }}), cast('delete' as {{ type_string() }}))
      and DBT_INTERNAL_DEST.dbt_valid_to is null
    then update
      set dbt_valid_to = DBT_INTERNAL_SOURCE.dbt_valid_to
    when not matched
      and cast(DBT_INTERNAL_SOURCE.dbt_change_type as {{ type_string() }}) = cast('insert' as {{ type_string() }})
    then insert ({{ insert_cols_csv }})
      values (
        {%- for column in insert_cols -%}
          DBT_INTERNAL_SOURCE.{{ column }}
          {%- if not loop.last %}, {% endif -%}
        {%- endfor -%}
      );
{% endmacro %}
