{% macro db2__load_csv_rows(model, agate_table) %}
    {% set cols_sql = get_seed_column_quoted_csv(model, agate_table.column_names) %}
    {% set values = [] %}
    
    {% for row in agate_table %}
        {% set row_values = [] %}
        {% for col_name in agate_table.column_names %}
            {% set col_val = adapter.quote_seed_value(row[col_name], model.config.quote_columns) %}
            {% do row_values.append(col_val) %}
        {% endfor %}
        {% do values.append("(" ~ row_values | join(", ") ~ ")") %}
    {% endfor %}
    
    {% set values_csv = values | join(",\n    ") %}
    
    {% set sql %}
        insert into {{ this.render() }} ({{ cols_sql }})
        values
            {{ values_csv }}
    {% endset %}
    
    {{ adapter.add_query(sql, abridge_sql_log=True) }}
    
    {# Return SQL so we can render it out into the compiled files #}
    {{ return(sql) }}
{% endmacro %}

