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

bad_sql = """
select bad sql here
"""

dupe_sql = """
select 1 as id, current_date as updated_at
union all
select 2 as id, current_date as updated_at
union all
select 3 as id, current_date as updated_at
union all
select 4 as id, current_date as updated_at
"""

good_sql = """
select 1 as id, current_date as updated_at
union all
select 2 as id, current_date as updated_at
union all
select 3 as id, current_date as updated_at
union all
select 4 as id, current_date as updated_at
"""

snapshots_good_sql = """
{% snapshot good_snapshot %}
    {{ config(target_schema=schema, target_database=database, strategy='timestamp', unique_key='id', updated_at='updated_at')}}
    select * from {{ schema }}.good
{% endsnapshot %}
"""

snapshots_bad_sql = """
{% snapshot good_snapshot %}
    {{ config(target_schema=schema, target_database=database, strategy='timestamp', unique_key='id', updated_at='updated_at_not_real')}}
    select * from {{ schema }}.good
{% endsnapshot %}
"""

schema_yml = """
version: 2
models:
- name: good
  columns:
  - name: updated_at
    data_tests:
    - not_null
- name: bad
  columns:
  - name: updated_at
    data_tests:
    - not_null
- name: dupe
  columns:
  - name: updated_at
    data_tests:
    - unique
"""

data_seed_good_csv = """a,b,c
1,2,3
"""

data_seed_bad_csv = """a,b,c
1,\2,3,a,a,a
"""
