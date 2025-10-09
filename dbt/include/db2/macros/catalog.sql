
{% macro db2__get_catalog(information_schema, schemas) -%}

  {%- call statement('catalog', fetch_result=True) -%}

    select
        SYSCAT.COLUMNS.TABSCHEMA as table_database,
        SYSCAT.COLUMNS.TABSCHEMA as table_schema,
        SYSCAT.COLUMNS.TABNAME as table_name,
        SYSCAT.TABLES.TYPE as table_type,
        SYSCAT.TABLES.REMARKS as table_comment,
        SYSCAT.COLUMNS.COLNAME as column_name,
        SYSCAT.COLUMNS.COLNO as column_index,
        SYSCAT.COLUMNS.TYPENAME as column_type,
        SYSCAT.COLUMNS.REMARKS as column_comment,
        SYSCAT.TABLES.OWNER as table_owner
    from
        SYSCAT.COLUMNS
        join SYSCAT.TABLES on
            SYSCAT.COLUMNS.TABSCHEMA = SYSCAT.TABLES.TABSCHEMA
            and SYSCAT.COLUMNS.TABNAME = SYSCAT.TABLES.TABNAME
    where
        SYSCAT.TABLES.TYPE in ('T', 'V')
        and SYSCAT.COLUMNS.TABSCHEMA in (
            {%- for schema in schemas -%}
                '{{ schema }}'
                {%- if not loop.last %}, {% endif -%}
            {%- endfor -%}
        )
    order by
        SYSCAT.COLUMNS.TABSCHEMA,
        SYSCAT.COLUMNS.TABNAME,
        SYSCAT.COLUMNS.COLNO

  {%- endcall -%}

  {{ return(load_result('catalog').table) }}

{%- endmacro %}
