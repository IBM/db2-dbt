{% macro test_positive_amount(model, column_name) %}
  SELECT *
  FROM {{ model }}
  WHERE {{ column_name }} <= 0
{% endmacro %}
