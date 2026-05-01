import os

import pytest

from tests.functional.projects import dbt_integration


@pytest.fixture(scope="class")
def dbt_integration_project():
    return dbt_integration()


@pytest.fixture(scope="class")
def dbt_profile_target():
    return {
        "type": "db2",
        "host": os.getenv("DBT_TEST_Db2_HOST", "hostname"),
        "port": int(os.getenv("DBT_TEST_Db2_PORT", 50000)),
        "user": os.getenv("DBT_TEST_Db2_USER", "ADMIN"),
        "pass": os.getenv("DBT_TEST_Db2_PASS", "password"),
        "dbname": os.getenv("DBT_TEST_Db2_DB", "TESTDBTINTEGRATION"),
        "schema": os.getenv("DBT_TEST_Db2_SCHEMA", "ADMIN"),
        "threads": int(os.getenv("DBT_TEST_Db2_THREADS", 4)),
    }
