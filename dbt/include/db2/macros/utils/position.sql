{% macro db2__position(substring_text, string_text) %}
    LOCATE({{ substring_text }}, {{ string_text }})
{% endmacro %}