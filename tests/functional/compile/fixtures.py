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

first_model_sql = """
select 1 as fun
"""

second_model_sql = """
{%- set columns = adapter.get_columns_in_relation(ref('first_model')) -%}
select
    *,
    {{ this.schema }} as schema
from {{ ref('first_model') }}
"""

first_ephemeral_model_sql = """
{{ config(materialized = 'ephemeral') }}
select 1 as fun
"""

second_ephemeral_model_sql = """
{{ config(materialized = 'ephemeral') }}
select * from {{ ref('first_ephemeral_model') }}
"""

third_ephemeral_model_sql = """
select * from {{ ref('second_ephemeral_model')}}
union all
select 2 as fun
"""

model_multiline_jinja = """
select {{
    1 + 1
}} as fun
"""

with_recursive_model_sql = """
{{ config(materialized = 'ephemeral') }}
with recursive t(n) as (
    select * from {{ ref('first_ephemeral_model') }}
  union all
    select n+1 from t where n < 100
)
select sum(n) from t;
"""

schema_yml = """
version: 2

models:
  - name: second_model
    description: "The second model"
    columns:
      - name: fun
        data_tests:
          - not_null
      - name: schema
        data_tests:
          - unique
"""
