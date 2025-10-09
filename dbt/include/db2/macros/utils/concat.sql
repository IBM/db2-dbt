{% macro db2__concat(fields) %}
    {{ fields|join(' || ') }}
{% endmacro %}
