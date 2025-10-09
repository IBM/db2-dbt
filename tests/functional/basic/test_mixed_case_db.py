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
                    "type": "netezza",
                    "threads": 4,
                    "host": "ssnzlite1.fyre.ibm.com",
                    "port": 5480,
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
