{% macro netezza__load_csv_rows(model, agate_table) %}
    {% set cols_sql = get_seed_column_quoted_csv(model, agate_table.column_names) %}
    {% set bindings = [] %}
    {% set et_options = adapter.get_et_options(model) %}
    {% set seed_file_path = adapter.get_seed_file_path(model) %}

    {% set sql %}
        insert into {{ this.render() }} ({{ cols_sql }})
        select * from external '{{ seed_file_path }}'
        using (
            REMOTESOURCE 'PYTHON'
            {{ et_options }}
        )
    {% endset %}

    {{ adapter.add_query(sql, bindings=bindings, abridge_sql_log=True) }}

    {# Return SQL so we can render it out into the compiled files #}
    {{ return(sql) }}
{% endmacro %}

