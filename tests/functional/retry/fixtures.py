#-------------------------------------------------------------------------------------------------#
#                      DISCLAIMER OF WARRANTIES AND LIMITATION OF LIABILITY                       #
#                                                                                                 #
#  (C) COPYRIGHT International Business Machines Corp. 2026 All Rights Reserved             #
#  Licensed Materials - Property of IBM                                                           #
#                                                                                                 #
#  US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP   #
#  Schedule Contract with IBM Corp.                                                               #
#                                                                                                 #
#  The following source code ("Sample") is owned by International Business Machines Corporation   #
#  or one of its subsidiaries ("IBM") and is copyrighted and licensed, not sold. You may use,     #
#  copy, modify, and distribute the Sample in any form without payment to IBM, for the purpose    #
#  of assisting you in the creation of Python applications using the ibm_db library.              #
#                                                                                                 #
#  The Sample code is provided to you on an "AS IS" basis, without warranty of any kind. IBM      #
#  HEREBY EXPRESSLY DISCLAIMS ALL WARRANTIES, EITHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT       #
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.    #
#  Some jurisdictions do not allow for the exclusion or limitation of implied warranties, so the  #
#  above limitations or exclusions may not apply to you. IBM shall not be liable for any damages  #
#  you suffer as a result of using, copying, modifying or distributing the Sample, even if IBM    #
#  has been advised of the possibility of such damages.                                           #
#-------------------------------------------------------------------------------------------------#

models__sample_model = """select 1 as id, baz as foo"""
models__second_model = """select 1 as id, 2 as bar"""

models__union_model = """
select foo + bar as sum3 from {{ ref('sample_model') }}
left join {{ ref('second_model') }} on sample_model.id = second_model.id
"""

schema_yml = """
models:
  - name: sample_model
    columns:
      - name: foo
        data_tests:
          - accepted_values:
              values: [3]
              quote: false
              config:
                severity: warn
  - name: second_model
    columns:
      - name: bar
        data_tests:
          - accepted_values:
              values: [3]
              quote: false
              config:
                severity: warn
  - name: union_model
    columns:
      - name: sum3
        data_tests:
          - accepted_values:
              values: [3]
              quote: false
"""

macros__alter_timezone_sql = """
{% macro alter_timezone(timezone='America/Los_Angeles') %}
{% set sql %}
    SET TimeZone='{{ timezone }}';
{% endset %}

{% do run_query(sql) %}
{% do log("Timezone set to: " + timezone, info=True) %}
{% endmacro %}
"""

simple_model = """
select null as id
"""

simple_schema = """
models:
  - name: some_model
    columns:
      - name: id
        data_tests:
          - not_null
"""
