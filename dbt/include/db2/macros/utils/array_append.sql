{% macro db2__array_append(array, new_element) -%}
    add_element({{ array }}, {{ new_element }})
{%- endmacro %}