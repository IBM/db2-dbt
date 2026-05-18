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

from dbt.exceptions import GitCheckoutError
from dbt.tests.util import (
    check_table_does_exist,
    check_table_does_not_exist,
    run_dbt,
)
import pytest

from tests.functional.exit_codes import fixtures


class BaseConfigProject:
    @pytest.fixture(scope="class")
    def models(self):
        return {
            "bad.sql": fixtures.bad_sql,
            "dupe.sql": fixtures.dupe_sql,
            "good.sql": fixtures.good_sql,
            "schema.yml": fixtures.schema_yml,
        }


class TestExitCodes(BaseConfigProject):
    @pytest.fixture(scope="class")
    def snapshots(self):
        return {"g.sql": fixtures.snapshots_good_sql}

    def test_exit_code_run_succeed(self, project):
        results = run_dbt(["run", "--model", "good"])
        assert len(results) == 1
        check_table_does_exist(project.adapter, "good")

    def test_exit_code_run_fail(self, project):
        results = run_dbt(["run", "--model", "bad"], expect_pass=False)
        assert len(results) == 1
        check_table_does_not_exist(project.adapter, "bad")

    def test_schema_test_pass(self, project):
        results = run_dbt(["run", "--model", "good"])
        assert len(results) == 1

        results = run_dbt(["test", "--model", "good"])
        assert len(results) == 1

    def test_schema_test_fail(self, project):
        results = run_dbt(["run", "--model", "dupe"])
        assert len(results) == 1

        results = run_dbt(["test", "--model", "dupe"], expect_pass=False)
        assert len(results) == 1

    def test_compile(self, project):
        results = run_dbt(["compile"])
        assert len(results) == 7


class TestExitCodesSnapshotFail(BaseConfigProject):
    @pytest.fixture(scope="class")
    def snapshots(self):
        return {"b.sql": fixtures.snapshots_bad_sql}

    def test_snapshot_fail(self, project):
        results = run_dbt(["run", "--model", "good"])
        assert len(results) == 1

        results = run_dbt(["snapshot"], expect_pass=False)
        assert len(results) == 1
        check_table_does_not_exist(project.adapter, "good_snapshot")


class TestExitCodesDeps:
    @pytest.fixture(scope="class")
    def packages(self):
        return {
            "packages": [
                {
                    "git": "https://github.com/dbt-labs/dbt-integration-project",
                    "revision": "dbt/1.0.0",
                }
            ]
        }

    def test_deps(self, project):
        results = run_dbt(["deps"])
        assert results is None


class TestExitCodesDepsFail:
    @pytest.fixture(scope="class")
    def packages(self):
        return {
            "packages": [
                {
                    "git": "https://github.com/dbt-labs/dbt-integration-project",
                    "revision": "bad-branch",
                },
            ]
        }

    def test_deps_fail(self, project):
        with pytest.raises(GitCheckoutError) as exc:
            run_dbt(["deps"])
        expected_msg = "Error checking out spec='bad-branch'"
        assert expected_msg in str(exc.value)


class TestExitCodesSeedFail:
    @pytest.fixture(scope="class")
    def seeds(self):
        return {"bad.csv": fixtures.data_seed_bad_csv}

    def test_seed(self, project):
        run_dbt(["seed"], expect_pass=False)
