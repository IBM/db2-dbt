{% macro db2__snapshot_string_as_time(timestamp) -%}
    {%- set result = "'" ~ timestamp ~ "'" ~ "::timestamp" -%}
    {{ return(result) }}
{%- endmacro %}
