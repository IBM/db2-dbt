{% macro db2__current_timestamp() -%}
  current_timestamp - (select TZOFFSET from _VT_PG_TIME_OFFSET)
{%- endmacro %}

{% macro db2__snapshot_string_as_time(timestamp) -%}
    {%- set result = "'" ~ timestamp ~ "'" ~ "::timestamp" -%}
    {{ return(result) }}
{%- endmacro %}
