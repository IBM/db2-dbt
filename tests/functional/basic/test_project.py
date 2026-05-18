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
from pathlib import Path

from dbt.tests.util import update_config_file, write_config_file
from dbt.exceptions import ProjectContractError
import pytest
import yaml

from tests.functional.utils import run_dbt


simple_model_sql = """
select true as my_column
"""

simple_model_yml = """
models:
  - name: simple_model
    description: "is sythentic data ok? my column:"
    columns:
      - name: my_column
        description: asked and answered
"""


class TestSchemaYmlVersionMissing:
    @pytest.fixture(scope="class")
    def models(self):
        return {"simple_model.sql": simple_model_sql, "simple_model.yml": simple_model_yml}

    def test_empty_version(self, project):
        run_dbt(["run"], expect_pass=True)


class TestProjectConfigVersionMissing:
    # default dbt_project.yml has config-version: 2
    @pytest.fixture(scope="class")
    def project_config_remove(self):
        return ["config-version"]

    def test_empty_version(self, project):
        run_dbt(["run"], expect_pass=True)


class TestProjectYamlVersionMissing:
    # default dbt_project.yml does not fill version

    def test_empty_version(self, project):
        run_dbt(["run"], expect_pass=True)


class TestProjectYamlVersionValid:
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {"version": "1.0.0"}

    def test_valid_version(self, project):
        run_dbt(["run"], expect_pass=True)


class TestProjectYamlVersionInvalid:
    def test_invalid_version(self, project):
        # we need to run it so the project gets set up first, otherwise we hit the semver error in setting up the test project
        run_dbt()
        update_config_file({"version": "invalid"}, "dbt_project.yml")
        with pytest.raises(ProjectContractError) as excinfo:
            run_dbt()
        assert "at path ['version']: 'invalid' is not valid under any of the given schemas" in str(
            excinfo.value
        )


class TestProjectDbtCloudConfig:
    @pytest.fixture(scope="class")
    def models(self):
        return {"simple_model.sql": simple_model_sql, "simple_model.yml": simple_model_yml}

    def test_dbt_cloud(self, project):
        run_dbt(["parse"], expect_pass=True)
        conf = yaml.safe_load(
            Path(os.path.join(project.project_root, "dbt_project.yml")).read_text()
        )
        assert conf == {
            "name": "test",
            "profile": "test",
            "flags": {"send_anonymous_usage_stats": False},
        }

        config = {
            "name": "test",
            "profile": "test",
            "flags": {"send_anonymous_usage_stats": False},
            "dbt-cloud": {
                "account_id": "123",
                "application": "test",
                "environment": "test",
                "api_key": "test",
            },
        }
        write_config_file(config, project.project_root, "dbt_project.yml")
        run_dbt(["parse"], expect_pass=True)
        conf = yaml.safe_load(
            Path(os.path.join(project.project_root, "dbt_project.yml")).read_text()
        )
        assert conf == config


class TestProjectDbtCloudConfigString:
    @pytest.fixture(scope="class")
    def models(self):
        return {"simple_model.sql": simple_model_sql, "simple_model.yml": simple_model_yml}

    def test_dbt_cloud_invalid(self, project):
        run_dbt()
        config = {"name": "test", "profile": "test", "dbt-cloud": "Some string"}
        update_config_file(config, "dbt_project.yml")
        expected_err = (
            "at path ['dbt-cloud']: 'Some string' is not valid under any of the given schemas"
        )
        with pytest.raises(ProjectContractError) as excinfo:
            run_dbt()
        assert expected_err in str(excinfo.value)
