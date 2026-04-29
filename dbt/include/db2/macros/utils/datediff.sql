{% macro db2__datediff(first_date, second_date, datepart) %}
    {% if datepart == 'year' %}
        (YEAR({{second_date}}) - YEAR({{first_date}}))
    {% elif datepart == 'quarter' %}
        ({{ datediff(first_date, second_date, 'year') }} * 4 + QUARTER({{second_date}}) - QUARTER({{first_date}}))
    {% elif datepart == 'month' %}
        ((YEAR({{second_date}}) - YEAR({{first_date}})) * 12 + (MONTH({{second_date}}) - MONTH({{first_date}})))
    {% elif datepart == 'day' %}
        (DAYS({{second_date}}) - DAYS({{first_date}}))
    {% elif datepart == 'week' %}
        ((DAYS({{second_date}}) - DAYS({{first_date}})) / 7)
    {% elif datepart == 'hour' %}
        ((DAYS({{second_date}}) - DAYS({{first_date}})) * 24 + (HOUR({{second_date}}) - HOUR({{first_date}})))
    {% elif datepart == 'minute' %}
        ({{ datediff(first_date, second_date, 'hour') }} * 60 + (MINUTE({{second_date}}) - MINUTE({{first_date}})))
    {% elif datepart == 'second' %}
        ({{ datediff(first_date, second_date, 'minute') }} * 60 + (SECOND({{second_date}}) - SECOND({{first_date}})))
    {% elif datepart == 'millisecond' %}
        ({{ datediff(first_date, second_date, 'second') }} * 1000 + (MICROSECOND({{second_date}}) / 1000 - MICROSECOND({{first_date}}) / 1000))
    {% elif datepart == 'microsecond' %}
        ({{ datediff(first_date, second_date, 'second') }} * 1000000 + (MICROSECOND({{second_date}}) - MICROSECOND({{first_date}})))
    {% else %}
        {{ exceptions.raise_compiler_error("Unsupported datepart for macro datediff in Db2: {!r}".format(datepart)) }}
    {% endif %}
{%- endmacro %}
