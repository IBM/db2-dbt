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

from dbt.tests.util import get_manifest
import pytest

from tests.functional.utils import run_dbt


model_sql = """
  select 1 as id from SYSIBM.SYSDUMMY1
"""


@pytest.fixture(scope="class")
def models():
    return {"model.sql": model_sql}


@pytest.fixture(scope="class")
def dbt_profile_data(unique_schema):
    return {
        "test": {
            "outputs": {
                "default": {
                    "type": "db2",
                    "threads": 4,
                    "host": "localhost",
                    "port": 50000,
                    "user": "ADMIN",
                    "pass": "password",
                    "dbname": "TESTDBTINTEGRATION",
                    "schema": unique_schema,
                },
            },
            "target": "default",
        },
    }


def test_basic(project_root, project):
    assert project.database == "TESTDBTINTEGRATION"

    # Tests that a project with a single model works
    results = run_dbt(["run"])
    assert len(results) == 1
    manifest = get_manifest(project_root)
    assert "model.test.model" in manifest.nodes
    # Running a second time works
    run_dbt(["run"])
