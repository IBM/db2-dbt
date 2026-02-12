{% macro db2__length(expression) -%}
    LENGTH({{ expression }})
{%- endmacro %}