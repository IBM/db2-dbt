{% macro db2__dateadd(datepart, interval, from_date_or_timestamp) %}
    {% if datepart == 'year' %}
        {{ from_date_or_timestamp }} + {{ interval }} YEARS
    {% elif datepart == 'quarter' %}
        {{ from_date_or_timestamp }} + ({{ interval }} * 3) MONTHS
    {% elif datepart == 'month' %}
        {{ from_date_or_timestamp }} + {{ interval }} MONTHS
    {% elif datepart == 'week' %}
        {{ from_date_or_timestamp }} + ({{ interval }} * 7) DAYS
    {% elif datepart == 'day' %}
        {{ from_date_or_timestamp }} + {{ interval }} DAYS
    {% elif datepart == 'hour' %}
        {{ from_date_or_timestamp }} + {{ interval }} HOURS
    {% elif datepart == 'minute' %}
        {{ from_date_or_timestamp }} + {{ interval }} MINUTES
    {% elif datepart == 'second' %}
        {{ from_date_or_timestamp }} + {{ interval }} SECONDS
    {% else %}
        {{ exceptions.raise_compiler_error("Unsupported datepart for macro dateadd in DB2: {!r}".format(datepart)) }}
    {% endif %}
{% endmacro %}
