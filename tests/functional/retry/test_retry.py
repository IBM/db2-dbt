from shutil import copytree, move

from dbt.contracts.results import RunStatus, TestStatus
from dbt.exceptions import TargetNotFoundError
from dbt.tests.util import rm_file, write_file
from dbt_common.exceptions import DbtRuntimeError
from tests.functional.utils import run_dbt
import pytest

from tests.functional.retry.fixtures import (
    macros__alter_timezone_sql,
    models__sample_model,
    models__second_model,
    models__union_model,
    schema_yml,
    simple_model,
    simple_schema,
)


class TestCustomTargetRetry:
    @pytest.fixture(scope="class")
    def models(self):
        return {
            "sample_model.sql": models__sample_model,
            "second_model.sql": models__second_model,
            "schema.yml": schema_yml,
        }

    def test_custom_target(self, project):
        run_dbt(["build", "--select", "second_model"])
        run_dbt(
            ["build", "--select", "sample_model", "--target-path", "target2"], expect_pass=False
        )

        # Regular retry - this is a no op because it's actually running `dbt build --select second_model`
        # agian because it's looking at the default target since the custom_target wasn't passed in
        results = run_dbt(["retry"])
        assert len(results) == 0

        # Retry with custom target after fixing the error
        fixed_sql = "select 1 as id, 1 as foo"
        write_file(fixed_sql, "models", "sample_model.sql")

        results = run_dbt(["retry", "--state", "target2"])
        expected_statuses = {
            "sample_model": RunStatus.Success,
            "accepted_values_sample_model_foo__False__3": TestStatus.Warn,
        }

        assert {n.node.name: n.status for n in results.results} == expected_statuses

        write_file(models__sample_model, "models", "sample_model.sql")


class TestRetry:
    @pytest.fixture(scope="class")
    def models(self):
        return {
            "sample_model.sql": models__sample_model,
            "second_model.sql": models__second_model,
            "union_model.sql": models__union_model,
            "schema.yml": schema_yml,
        }

    @pytest.fixture(scope="class")
    def macros(self):
        return {"alter_timezone.sql": macros__alter_timezone_sql}

    def test_no_previous_run(self, project):
        with pytest.raises(
            DbtRuntimeError, match="Could not find previous run in 'target' target directory"
        ):
            run_dbt(["retry"])

        with pytest.raises(
            DbtRuntimeError, match="Could not find previous run in 'walmart' target directory"
        ):
            run_dbt(["retry", "--state", "walmart"])

    def test_warn_error(self, project):
        # Our test command should succeed when run normally...
        results = run_dbt(["build", "--select", "second_model"])

        # ...but it should fail when run with warn-error, due to a warning...
        results = run_dbt(["--warn-error", "build", "--select", "second_model"], expect_pass=False)

        expected_statuses = {
            "second_model": RunStatus.Success,
            "accepted_values_second_model_bar__False__3": TestStatus.Fail,
        }

        assert {n.node.name: n.status for n in results.results} == expected_statuses

        # Retry regular, should pass
        run_dbt(["retry"])

        # Retry with --warn-error, should fail
        run_dbt(["--warn-error", "retry"], expect_pass=False)

    def test_removed_file(self, project):
        run_dbt(["build"], expect_pass=False)

        rm_file("models", "sample_model.sql")

        with pytest.raises(
            TargetNotFoundError, match="depends on a node named 'sample_model' which was not found"
        ):
            run_dbt(["retry"], expect_pass=False)

        write_file(models__sample_model, "models", "sample_model.sql")

    def test_removed_file_leaf_node(self, project):
        write_file(models__sample_model, "models", "third_model.sql")
        run_dbt(["build"], expect_pass=False)

        rm_file("models", "third_model.sql")
        with pytest.raises(ValueError, match="Couldn't find model 'model.test.third_model'"):
            run_dbt(["retry"], expect_pass=False)


class TestRetryResourceType:
    @pytest.fixture(scope="class")
    def models(self):
        return {
            "null_model.sql": simple_model,
            "schema.yml": simple_schema,
        }

    def test_resource_type(self, project):
        # test multiple options in single string
        results = run_dbt(["build", "--select", "null_model", "--resource-type", "test model"])
        assert len(results) == 1

        # nothing to do
        results = run_dbt(["retry"])
        assert len(results) == 0

        # test multiple options in multiple args
        results = run_dbt(
            [
                "build",
                "--select",
                "null_model",
                "--resource-type",
                "test",
                "--resource-type",
                "model",
            ]
        )
        assert len(results) == 1

        # nothing to do
        results = run_dbt(["retry"])
        assert len(results) == 0

        # test single all option
        results = run_dbt(["build", "--select", "null_model", "--resource-type", "all"])
        assert len(results) == 1

        # nothing to do
        results = run_dbt(["retry"])
        assert len(results) == 0


class TestRetryVars:
    @pytest.fixture(scope="class")
    def models(self):
        return {
            "sample_model.sql": "select {{ var('myvar_a', '1') + var('myvar_b', '2') }} as mycol",
        }

    def test_retry(self, project):
        # pass because default vars works
        run_dbt(["run"])
        run_dbt(["run", "--vars", '{"myvar_a": "12", "myvar_b": "3 4"}'], expect_pass=False)
        # fail because vars are invalid, this shows that the last passed vars are being used
        # instead of using the default vars
        run_dbt(["retry"], expect_pass=False)
        results = run_dbt(["retry", "--vars", '{"myvar_a": "12", "myvar_b": "34"}'])
        assert len(results) == 1


class TestRetryFullRefresh:
    @pytest.fixture(scope="class")
    def models(self):
        return {
            "sample_model.sql": "{% if flags.FULL_REFRESH %} this is invalid sql {% else %} select 1 as mycol {% endif %}",
        }

    def test_retry(self, project):
        # This run should fail with invalid sql...
        run_dbt(["run", "--full-refresh"], expect_pass=False)
        # ...and so should this one, since the effect of the full-refresh parameter should persist.
        results = run_dbt(["retry"], expect_pass=False)
        assert len(results) == 1
