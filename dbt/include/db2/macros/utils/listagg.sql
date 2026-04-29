{% macro db2__listagg(measure, delimiter_text, order_by_clause, limit_num) -%}
    {% if limit_num -%}
        {{ exceptions.raise_compiler_error("Db2 does not support 'limit_num' argument in LISTAGG function") }}
    {%- endif %}
    
    {%- if order_by_clause -%}
        listagg({{ measure }}, {{ delimiter_text }}) within group (order by {{ order_by_clause }})
    {%- else -%}
        listagg({{ measure }}, {{ delimiter_text }})
    {%- endif -%}
{%- endmacro -%}
