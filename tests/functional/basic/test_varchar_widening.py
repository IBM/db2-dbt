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

import os

from dbt.tests.util import check_relations_equal
import pytest

from tests.functional.utils import run_dbt


incremental_sql = """
{{
  config(
    materialized = "incremental"
  )
}}

select * from {{ this.schema }}.seed

{% if is_incremental() %}

    where id > (select max(id) from {{this}})

{% endif %}
"""

materialized_sql = """
{{
  config(
    materialized = "table"
  )
}}

select * from {{ this.schema }}.seed
"""


@pytest.fixture(scope="class")
def models():
    return {"incremental.sql": incremental_sql, "materialized.sql": materialized_sql}


def test_varchar_widening(project):
    path = os.path.join(project.test_data_dir, "varchar10_seed.sql")
    project.run_sql_file(path)

    results = run_dbt(["run"])
    assert len(results) == 2

    check_relations_equal(project.adapter, ["seed", "incremental"])
    check_relations_equal(project.adapter, ["seed", "materialized"])

    path = os.path.join(project.test_data_dir, "varchar300_seed.sql")
    project.run_sql_file(path)

    results = run_dbt(["run"])
    assert len(results) == 2

    check_relations_equal(project.adapter, ["seed", "incremental"])
    check_relations_equal(project.adapter, ["seed", "materialized"])
